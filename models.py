# app/models.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Hadith(Base):
    """Database model for storing Hadith data"""
    __tablename__ = "hadith"
    
    id = Column(Integer, primary_key=True, index=True)
    text_english = Column(Text, nullable=False)
    text_arabic = Column(Text)
    collection = Column(String(100), nullable=False)
    book = Column(String(200))
    chapter = Column(String(200))
    hadith_number = Column(Integer)
    grade = Column(String(50))
    narrator = Column(String(500))
    theme = Column(String(200))
    keywords = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class MoodMapping(Base):
    """Database model for mood-to-theme mappings"""
    __tablename__ = "mood_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    mood_keyword = Column(String(100), nullable=False)
    emotion_category = Column(String(100))
    related_themes = Column(Text)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Hadith(Base):
    __tablename__ = "hadiths"

    id = Column(Integer, primary_key=True, index=True)
    collection = Column(String, index=True)   # e.g., Sahih Bukhari
    volume = Column(String, nullable=True)
    book = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    narrator = Column(String, nullable=True)
    text = Column(Text, nullable=False)
