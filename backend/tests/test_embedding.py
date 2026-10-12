
from app.services.embedding_service import (
    generate_embedding,
    generate_embeddings,
)

text = "I completed a database certification."

# Generate one embedding.
vector = generate_embedding(text)

print("Input text:", text)
print("Vector dimensions:", len(vector))
print("First 10 values:", vector[:10])

assert len(vector) == 384

# Generate embeddings for multiple text chunks.
chunks = [
    "I completed a database certification.",
    "I learned Python programming.",
    "I enjoy playing badminton.",
]

vectors = generate_embeddings(chunks)

print("\nNumber of chunks:", len(chunks))
print("Number of embeddings:", len(vectors))
print("Dimensions per embedding:", len(vectors[0]))

assert len(vectors) == len(chunks)
assert all(len(v) == 384 for v in vectors)

print("\nEmbedding tests passed!")
