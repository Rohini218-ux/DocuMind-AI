
from pathlib import Path

from app.services.document_processing_service import process_pdf

# Find the backend directory from this test file.
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "storage" / "pdfs"

print("Backend directory:", BASE_DIR)
print("Expected PDF folder:", UPLOAD_DIR)
print("Folder exists:", UPLOAD_DIR.exists())

if UPLOAD_DIR.exists():
    pdf_files = list(UPLOAD_DIR.glob("*.pdf"))
    print("PDF files found:", len(pdf_files))

    for pdf in pdf_files:
        print("Found:", pdf.name)
        print("Full path:", pdf.resolve())
else:
    pdf_files = []

if not pdf_files:
    print("\nNo PDFs found in the expected folder.")
    print("Check the PowerShell search results.")
else:
    pdf_path = pdf_files[0]

    print("\nProcessing:", pdf_path.resolve())

    result = process_pdf(pdf_path)

    print("Pages:", result["page_count"])
    print("Characters:", result["character_count"])
    print("Chunks:", result["chunk_count"])

    for index, chunk in enumerate(result["chunks"], start=1):
        print(f"\n--- Chunk {index} ---")
        print(chunk[:300])

    print("\nDocument processing completed!")
