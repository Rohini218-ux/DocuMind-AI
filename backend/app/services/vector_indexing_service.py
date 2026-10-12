
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.models import DocumentChunk
from app.services.vector_store_service import VectorStore


FAISS_DIRECTORY = Path("storage/faiss")


def rebuild_vector_store(db: Session) -> VectorStore:
    """Rebuild FAISS from the authoritative PostgreSQL chunk records."""

    rows = (
        db.query(DocumentChunk)
        .order_by(DocumentChunk.id)
        .all()
    )

    store = VectorStore()

    if rows:
        store.add_chunks(
            chunks=[row.content for row in rows],
            chunk_ids=[row.id for row in rows],
            document_ids=[row.document_id for row in rows],
        )

    store.save(FAISS_DIRECTORY)
    return store
