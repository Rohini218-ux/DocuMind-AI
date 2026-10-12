
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

texts = [
    "I completed a database certification.",
    "I earned a certificate in database management.",
    "I enjoy playing badminton.",
]

# Convert the sentences into embedding vectors
embeddings = model.encode(texts, normalize_embeddings=True)

# Compare the first sentence with every sentence
scores = cosine_similarity(
    [embeddings[0]],
    embeddings
)[0]

print("Reference sentence:", texts[0])
print()

for text, score in zip(texts, scores):
    print(f"Similarity: {score:.4f} | {text}")
