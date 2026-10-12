
from pathlib import Path

import pymupdf

from app.services.text_service import clean_text


def extract_pdf_text(file_path: Path) -> dict:
    """Extract and clean text from each page of a PDF."""

    with pymupdf.open(file_path) as pdf:
        page_texts = []

        for page in pdf:
            text = page.get_text(sort=True)
            page_texts.append(text)

        combined_text = "\n".join(page_texts)
        cleaned_text = clean_text(combined_text)

        return {
            "page_count": len(pdf),
            "text": cleaned_text,
        }
