# populate_data.py - Run this once to add sample data
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Hadith, MoodMapping

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Sample Hadith data (famous authentic Hadith)
SAMPLE_HADITH = [
    {
        "text_english": "Actions are but by intention, and every man shall have only that which he intended.",
        "text_arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى",
        "collection": "Sahih Bukhari",
        "book": "Book of Revelation",
        "chapter": "How the Divine Inspiration started",
        "hadith_number": 1,
        "grade": "Sahih",
        "narrator": "Umar ibn al-Khattab",
        "theme": "intention",
        "keywords": "actions, intention, niyyah, purpose"
    },
    {
        "text_english": "Allah does not burden a soul beyond that it can bear.",
        "text_arabic": "لاَ يُكَلِّفُ اللَّهُ نَفْسًا إِلاَّ وُسْعَهَا",
        "collection": "Quran Reference",
        "book": "Surah Al-Baqarah",
        "chapter": "Verse 286",
        "hadith_number": 286,
        "grade": "Sahih",
        "narrator": "Quranic Verse",
        "theme": "patience",
        "keywords": "burden, capability, patience, strength"
    }
]

# Sample mood mappings
MOOD_MAPPINGS = [
    {
        "mood_keyword": "sad",
        "emotion_category": "sadness",
        "related_themes": "patience, hope, helping",
        "priority": 1
    },
    {
        "mood_keyword": "angry",
        "emotion_category": "anger",
        "related_themes": "anger, patience, speech",
        "priority": 1
    }
]

def populate_database():
    """Add sample data to database"""
    try:
        # Add Hadith
        print("Adding sample Hadith...")
        for hadith_data in SAMPLE_HADITH:
            hadith = Hadith(**hadith_data)
            db.add(hadith)
        
        # Add mood mappings
        print("Adding mood mappings...")
        for mood_data in MOOD_MAPPINGS:
            mood = MoodMapping(**mood_data)
            db.add(mood)
        
        # Commit all changes
        db.commit()
        print(f"✅ Successfully added {len(SAMPLE_HADITH)} Hadith and {len(MOOD_MAPPINGS)} mood mappings!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()