import os
import json
import argparse
from sqlalchemy.orm import Session

from app.database import engine, Base
from app.models import Hadith
from app.utils.text_processor import normalize_text

# ✅ Ensure tables exist
Base.metadata.create_all(bind=engine)


def find_json_file() -> str | None:
    file_paths = [
        r"C:\Users\rushi\hadithakhi resources\code ha\Complete-Sahih-Bukhari-Json\sahih_bukhari.json",
        r"C:\Users\rushi\hadithakhi resources\code ha\backend\data\hadith_collections\sahih_bukhari.json",
        r"C:\Users\rushi\hadithakhi resources\code ha\backend\data\bukhari.json",
    ]
    return next((f for f in file_paths if os.path.exists(f)), None)


def load_bukhari_data(volume_number: int | None = None) -> None:
    file_path = find_json_file()
    if not file_path:
        print("❌ Sahih Bukhari JSON file not found!")
        return

    print(f"📖 Reading JSON file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_loaded, total_skipped = 0, 0

    with Session(engine) as session:
        for volume in data:
            volume_name = volume.get("name", "Unknown Volume")

            if volume_number and f"Volume {volume_number}" not in volume_name:
                continue

            print(f"\n📚 Processing {volume_name}...")
            volume_loaded, volume_skipped = 0, 0

            for book in volume.get("books", []):
                book_name = book.get("name", "Unknown Book")

                for hadith in book.get("hadiths", []):
                    try:
                        new_hadith = Hadith(
                            collection="Sahih Bukhari",
                            volume=volume_name,
                            book=book_name,
                            reference=hadith.get("info") or "",
                            narrator=hadith.get("by") or "",
                            text=normalize_text(hadith.get("text") or ""),
                        )
                        session.add(new_hadith)
                        volume_loaded += 1
                    except Exception as e:
                        print(f"⚠️ Skipped hadith due to error: {e}")
                        volume_skipped += 1

            session.commit()
            print(f"   ✅ Loaded: {volume_loaded} | ⚠️ Skipped: {volume_skipped}")

            total_loaded += volume_loaded
            total_skipped += volume_skipped

    print("\n============================================================")
    print("🎉 INTEGRATION COMPLETED!")
    print(f"✅ Successfully loaded: {total_loaded} hadith")
    print(f"⚠️ Skipped: {total_skipped} hadith")
    if total_loaded + total_skipped > 0:
        success_rate = round((total_loaded / (total_loaded + total_skipped)) * 100, 2)
        print(f"📈 Success rate: {success_rate}%")
    else:
        print("📈 No hadith processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Sahih Bukhari hadith into database")
    parser.add_argument("--volume", type=int, help="Load only a specific volume (e.g., --volume 1)")
    args = parser.parse_args()

    load_bukhari_data(volume_number=args.volume)
