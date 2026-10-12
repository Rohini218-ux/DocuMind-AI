
from app.services.chunk_service import chunk_text

sample_text = (
    "DocuMind AI processes documents. "
    "It extracts text from PDFs. "
    "The extracted text is cleaned. "
    "Then the text is divided into chunks. "
    "These chunks can later be converted into embeddings."
)

chunks = chunk_text(
    sample_text,
    chunk_size=60,
    overlap=10,
)

for index, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {index}:")
    print(chunk)

assert "".join(chunks) != ""
assert all(chunks)
assert chunk_text("") == []

print("\nChunking test passed!")
