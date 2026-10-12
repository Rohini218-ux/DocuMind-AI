
from app.database.connection import SessionLocal
from app.database.models import DocumentChunk
from app.services.vector_indexing_service import rebuild_vector_store
from app.services.vector_store_service import VectorStore, generate_embeddings

db = SessionLocal()

try:
    count = db.query(DocumentChunk).count()
    print("Chunks found in PostgreSQL:", count)

    if count == 0:
        print("No chunks found. Upload and process a PDF first.")
    else:
        # Build a persistent index using actual database records.
        store = rebuild_vector_store(db)
        print("Vectors indexed:", store.index.ntotal)

        # Verify the saved index can be restored.
        restored = VectorStore.load(
            __import__(
                "app.services.vector_indexing_service",
                fromlist=["FAISS_DIRECTORY"],
            ).FAISS_DIRECTORY
        )

        assert restored.index.ntotal == count

        print("Real database index test passed!")

finally:
    db.close()
