
from pathlib import Path

from app.services.pdf_service import extract_pdf_text
from app.services.chunk_service import chunk_text


def process_pdf(file_path: Path) -> dict:
    """Extract, clean, and chunk a PDF."""

    result = extract_pdf_text(file_path)
    extracted_text = result["text"]

    if not extracted_text.strip():
        raise ValueError("No extractable text found in PDF")

    chunks = chunk_text(
        extracted_text,
        chunk_size=1000,
        overlap=150,
    )

    return {
        "page_count": result["page_count"],
        "character_count": len(extracted_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
