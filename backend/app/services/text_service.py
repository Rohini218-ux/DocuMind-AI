
import re


def clean_text(text: str) -> str:
    """Normalize extracted PDF text."""

    # Normalize Windows and old-style line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace non-breaking spaces with normal spaces.
    text = text.replace("\u00a0", " ")

    # Remove trailing whitespace from each line.
    lines = [line.strip() for line in text.split("\n")]

    # Rejoin lines and collapse repeated spaces and tabs.
    text = "\n".join(lines)
    text = re.sub(r"[ \t]+", " ", text)

    # Limit excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
