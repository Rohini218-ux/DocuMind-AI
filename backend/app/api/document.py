
from pathlib import Path
from uuid import uuid4

import pymupdf
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import Document, DocumentChunk, User
from app.schemas.document import DocumentResponse
from app.services.chunk_storage_service import save_document_chunks
from app.services.document_processing_service import process_pdf
from app.services.pdf_service import extract_pdf_text
from app.services.vector_indexing_service import rebuild_vector_store
from app.utils.auth import get_current_user


router = APIRouter(prefix="/documents", tags=["Documents"])

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "storage" / "pdfs"
MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_path = None
    document = None

    try:
        # 1. Validate the uploaded file.
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed",
            )

        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content type must be application/pdf",
            )

        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size must not exceed 10 MB",
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF signature",
            )

        # 2. Save the PDF file.
        stored_filename = f"{uuid4()}.pdf"
        file_path = UPLOAD_DIR / stored_filename
        file_path.write_bytes(content)

        # 3. Save the document metadata.
        document = Document(
            owner_id=current_user.id,
            original_filename=Path(file.filename).name,
            stored_filename=stored_filename,
            file_size=len(content),
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 4. Extract text and generate chunks.
        processed = process_pdf(file_path)
        chunks = processed["chunks"]

        if not chunks:
            raise ValueError("No extractable text chunks found")

        # 5. Save chunks in PostgreSQL.
        saved_count = save_document_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        # 6. Rebuild and persist the FAISS index.
        store = rebuild_vector_store(db)

        return {
            "message": "PDF uploaded and indexed successfully",
            "document_id": document.id,
            "filename": document.original_filename,
            "size_bytes": document.file_size,
            "uploaded_by": document.owner_id,
            "created_at": document.created_at,
            "page_count": processed["page_count"],
            "chunks_saved": saved_count,
            "vectors_indexed": store.index.ntotal,
        }

    except HTTPException:
        # Preserve expected HTTP errors.
        raise

    except Exception as exc:
        # Roll back any active database transaction.
        db.rollback()

        # Remove the failed document and its chunks.
        if document is not None and document.id is not None:
            try:
                db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document.id
                ).delete(synchronize_session=False)

                db.query(Document).filter(
                    Document.id == document.id
                ).delete(synchronize_session=False)

                db.commit()
            except SQLAlchemyError:
                db.rollback()

        # Remove the uploaded file.
        if file_path is not None:
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                pass

        # Try to restore FAISS from the remaining database records.
        try:
            rebuild_vector_store(db)
        except Exception:
            # The index may require recovery if rebuilding also fails.
            pass

        # Log the actual error in the server terminal.
        print(f"Document upload/indexing failed: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save or index the document",
        ) from None

    finally:
        await file.close()


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )

    result = db.execute(statement)
    documents = result.scalars().all()

    return documents


@router.get("/{document_id}/text")
def get_document_text(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None or document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = UPLOAD_DIR / document.stored_filename

    try:
        result = extract_pdf_text(file_path)
    except (pymupdf.FileDataError, OSError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read this PDF",
        ) from None

    if not result["text"].strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No extractable text found. This PDF may require OCR.",
        )

    return {
        "document_id": document.id,
        "filename": document.original_filename,
        "page_count": result["page_count"],
        "character_count": len(result["text"]),
        "text": result["text"],
    }
