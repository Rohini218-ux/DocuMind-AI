
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.document_processing_service import process_pdf
from app.services.chunk_storage_service import save_document_chunks
from app.services.vector_store_service import VectorStore


def index_document(
    db: Session,
    document_id: int,
    file_path: Path,
    vector_store: VectorStore,
) -> dict:
    """Extract, chunk, store and index a PDF."""

    # 1. Extract text and split it into chunks.
    result = process_pdf(file_path)
    chunks = result["chunks"]

    if not chunks:
        raise ValueError("No text chunks were generated")

    # 2. Save chunk text and metadata in PostgreSQL.
    saved_count = save_document_chunks(
        db=db,
        document_id=document_id,
        chunks=chunks,
    )

    # 3. Add chunks to the FAISS index.
    vector_store.add_chunks(chunks)

    return {
        "document_id": document_id,
        "chunk_count": saved_count,
        "page_count": result["page_count"],
        "character_count": result["character_count"],
    }
