import json

def normalize_bukhari(raw_path: str, normalized_path: str):
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []

    for i, item in enumerate(data, start=1):
        # If your file is just a list of strings
        if isinstance(item, str):
            normalized.append({
                "hadith_number": i,
                "english_text": item,
                "arabic_text": None,
                "book": None,
                "chapter": None,
                "narrator": None,
                "grade": "Sahih",
                "theme": None,
                "keywords": None
            })
        # If your file is dicts with some structure
        elif isinstance(item, dict):
            normalized.append({
                "hadith_number": item.get("hadith_number", i),
                "english_text": item.get("english_text") or item.get("text") or "",
                "arabic_text": item.get("arabic_text"),
                "book": item.get("book"),
                "chapter": item.get("chapter"),
                "narrator": item.get("narrator"),
                "grade": item.get("grade", "Sahih"),
                "theme": item.get("theme"),
                "keywords": item.get("keywords")
            })

    with open(normalized_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    print(f"✅ Normalized {len(normalized)} hadiths and saved to {normalized_path}")


if __name__ == "__main__":
    normalize_bukhari(
        "backend/data/hadith_collections/raw_sahih_bukhari.json",
        "backend/data/hadith_collections/sahih_bukhari.json"
    )
