
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """Convert text into a 384-dimensional embedding vector."""

    if not text.strip():
        raise ValueError("Text cannot be empty")

    vector = model.encode(
        text,
        normalize_embeddings=True,
    )

    return vector.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert multiple text chunks into embedding vectors."""

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Texts cannot contain empty strings")

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return vectors.tolist()
