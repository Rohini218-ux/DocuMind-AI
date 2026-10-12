
from app.services.vector_store_service import VectorStore


def test_vector_store_search():
    store = VectorStore()

    chunks = [
        "I completed a database certification.",
        "I learned Python programming and data analysis.",
        "I enjoy playing badminton on weekends.",
    ]

    chunk_ids = [1, 2, 3]
    document_ids = [1, 1, 1]

    store.add_chunks(
        chunks=chunks,
        chunk_ids=chunk_ids,
        document_ids=document_ids,
    )

    query = "Which database qualification did I complete?"
    results = store.search(query, top_k=3)

    assert len(results) == 3
    assert results[0]["chunk_id"] == 1
    assert results[0]["document_id"] == 1
    assert results[0]["similarity"] > results[1]["similarity"]
