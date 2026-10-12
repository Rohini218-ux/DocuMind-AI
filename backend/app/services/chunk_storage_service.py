
from sqlalchemy.orm import Session

from app.database.models import DocumentChunk


def save_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
) -> int:
    """Save the text chunks belonging to one document."""

    if not chunks:
        return 0

    records = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
        )
        for index, chunk in enumerate(chunks)
        if chunk.strip()
    ]

    try:
        db.add_all(records)
        db.commit()
        return len(records)
    except Exception:
        db.rollback()
        raise
