import re

def normalize_text(text: str) -> str:
    """Cleans and normalizes hadith text."""
    if not text:
        return ""
    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    # remove strange characters if any
    text = text.replace("\u200c", "").replace("\u200b", "")
    return text
