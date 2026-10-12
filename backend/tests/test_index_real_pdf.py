
from pathlib import Path

from app.database.connection import SessionLocal
from app.database.models import Document
from app.services.document_processing_service import process_pdf
from app.services.chunk_storage_service import save_document_chunks
from app.services.vector_indexing_service import rebuild_vector_store

PDF_DIRECTORY = Path("storage/pdfs")

db = SessionLocal()

try:
    document = (
        db.query(Document)
        .filter(Document.owner_id == 5)
        .first()
    )

    if document is None:
        raise RuntimeError("No document found for user ID 5.")

    pdf_path = PDF_DIRECTORY / document.stored_filename

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found at: {pdf_path}"
        )

    # Extract the PDF text and create chunks.
    processed = process_pdf(pdf_path)
    chunks = processed["chunks"]

    print("PDF:", document.original_filename)
    print("Pages:", processed["page_count"])
    print("Chunks generated:", len(chunks))

    if not chunks:
        raise ValueError("No text chunks were generated.")

    # Remove previously saved test chunks for this document.
    # Only do this for the document selected above.
    from app.database.models import DocumentChunk

    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete(synchronize_session=False)
    db.commit()

    # Save the actual PDF chunks.
    saved = save_document_chunks(
        db=db,
        document_id=document.id,
        chunks=chunks,
    )

    print("Real chunks saved:", saved)

    # Rebuild FAISS from PostgreSQL.
    store = rebuild_vector_store(db)
    print("Vectors indexed:", store.index.ntotal)

    print("Real PDF indexing completed!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
