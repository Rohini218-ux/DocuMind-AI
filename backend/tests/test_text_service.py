
from app.services.text_service import clean_text

sample = "  DocuMind   AI  \r\n\r\n\r\n Document    Processing  "

result = clean_text(sample)

print(result)
assert result == "DocuMind AI\n\nDocument Processing"

print("Text cleaning test passed!")
