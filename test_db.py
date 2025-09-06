from app.database import SessionLocal
from app.models import Hadith

db = SessionLocal()
print("Hadith count:", db.query(Hadith).count())
