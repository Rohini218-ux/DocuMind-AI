
from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.services.vector_indexing_service import FAISS_DIRECTORY
from app.services.vector_store_service import VectorStore


def search_documents(
    db: Session,
    user_id: int,
    query: str,
    top_k: int = 3,
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    # Load the persistent FAISS index.
    store = VectorStore.load(FAISS_DIRECTORY)

    if store.index.ntotal == 0:
        return []

    # Retrieve candidate chunks from the vector index.
    candidates = store.search(
        query,
        top_k=min(top_k * 5, store.index.ntotal),
    )

    results = []

    for candidate in candidates:

        # Retrieve the chunk and its associated document.
        row = (
            db.query(DocumentChunk, Document)
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .filter(
                DocumentChunk.id == candidate["chunk_id"],
                Document.owner_id == user_id,
            )
            .first()
        )

        # Skip chunks that don't belong to this user.
        if row is None:
            continue

        chunk, document = row

        results.append({
            "document_id": document.id,
            "document_name": document.original_filename,
            "chunk_id": chunk.id,
            "content": chunk.content,
            "similarity": float(candidate["similarity"]),
        })

        if len(results) >= top_k:
            break

    return results
