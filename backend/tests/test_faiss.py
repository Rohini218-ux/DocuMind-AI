
import faiss
import numpy as np

# Three example vectors, each with 3 dimensions.
vectors = np.array(
    [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 0.0, 1.0],
    ],
    dtype="float32",
)

# Create a FAISS index using inner product.
# These vectors are normalized, so inner product equals cosine similarity.
index = faiss.IndexFlatIP(3)

# Add the vectors to the index.
index.add(vectors)

# Search using the first vector.
query = np.array([[1.0, 0.0, 0.0]], dtype="float32")
scores, indices = index.search(query, k=3)

print("Total vectors stored:", index.ntotal)
print("\nSearch results:")

for score, idx in zip(scores[0], indices[0]):
    print(f"Vector index: {idx}, similarity: {score:.4f}")

assert index.ntotal == 3
assert indices[0][0] == 0

print("\nFAISS test passed!")
