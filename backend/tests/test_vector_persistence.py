
from pathlib import Path
from app.services.vector_store_service import VectorStore

test_dir = Path("storage/faiss_test")

chunks = [
    "I completed a database certification.",
    "I learned Python programming.",
    "I enjoy playing badminton.",
]

# Temporary IDs for testing only.
chunk_ids = [101, 102, 103]
document_ids = [10, 10, 11]

store = VectorStore()
store.add_chunks(chunks, chunk_ids, document_ids)
store.save(test_dir)

# Simulate restarting the application.
restored = VectorStore.load(test_dir)

print("Vectors restored:", restored.index.ntotal)

results = restored.search(
    "Which database certification did I complete?",
    top_k=3,
)

for result in results:
    print(result)

assert restored.index.ntotal == 3
assert results[0]["chunk_id"] == 101
assert results[0]["document_id"] == 10

print("FAISS persistence test passed!")
