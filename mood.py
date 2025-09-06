# app/api/mood.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Hadith, MoodMapping
from pydantic import BaseModel
import random
import re

router = APIRouter()

class MoodRequest(BaseModel):
    mood: str

class MoodResponse(BaseModel):
    mood_detected: str
    hadith: dict
    relevance_explanation: str
    personal_reflection: str

class MoodHadithMatcher:
    def __init__(self, db: Session):
        self.db = db
        
    def find_hadith_for_mood(self, mood_input: str) -> dict:
        """Find relevant hadith based on mood/feeling"""
        # Extract mood keywords from user input
        mood_keywords = self.extract_mood_keywords(mood_input.lower())
        
        # Find matching themes based on mood
        relevant_themes = self.get_relevant_themes(mood_keywords)
        
        # Find hadith matching these themes
        matching_hadith = self.find_matching_hadith(relevant_themes)
        
        if not matching_hadith:
            # Fallback to general inspirational hadith
            matching_hadith = self.db.query(Hadith).limit(5).all()
        
        # Select the best hadith for this mood
        selected_hadith = self.select_best_hadith(matching_hadith, mood_keywords)
        
        return self.format_mood_response(selected_hadith, mood_input, mood_keywords)
    
    def extract_mood_keywords(self, text: str) -> list:
        """Extract mood-related keywords from user input"""
        mood_patterns = {
            'sad': ['sad', 'depressed', 'down', 'upset', 'heartbroken', 'crying', 'grief'],
            'angry': ['angry', 'mad', 'furious', 'rage', 'frustrated', 'annoyed', 'irritated'],
            'worried': ['worried', 'anxious', 'stressed', 'nervous', 'scared', 'afraid', 'concerned'],
            'lazy': ['lazy', 'unmotivated', 'tired', 'exhausted', 'procrastinating', 'sluggish'],
            'grateful': ['grateful', 'thankful', 'blessed', 'appreciative', 'happy', 'joyful'],
            'lonely': ['lonely', 'alone', 'isolated', 'abandoned', 'friendless'],
            'confused': ['confused', 'lost', 'uncertain', 'doubtful', 'puzzled'],
            'hopeless': ['hopeless', 'despair', 'giving up', 'defeated', 'overwhelmed']
        }
        
        detected_moods = []
        for mood_category, keywords in mood_patterns.items():
            if any(keyword in text for keyword in keywords):
                detected_moods.append(mood_category)
        
        return detected_moods if detected_moods else ['general']
    
    def get_relevant_themes(self, mood_keywords: list) -> list:
        """Get hadith themes relevant to the detected moods"""
        all_themes = []
        
        for mood in mood_keywords:
            # Check our mood mapping database
            mapping = self.db.query(MoodMapping).filter(
                MoodMapping.mood_keyword == mood
            ).first()
            
            if mapping:
                themes = [theme.strip() for theme in mapping.related_themes.split(',')]
                all_themes.extend(themes)
        
        # If no mappings found, use default themes for common moods
        if not all_themes:
            default_themes = {
                'sad': ['patience', 'helping', 'hope'],
                'angry': ['anger', 'patience', 'speech'],
                'worried': ['patience', 'helping'],
                'lazy': ['intention', 'helping'],
                'grateful': ['kindness', 'charity'],
                'lonely': ['brotherhood', 'helping'],
                'confused': ['patience', 'intention'],
                'hopeless': ['patience', 'helping', 'hope']
            }
            
            for mood in mood_keywords:
                if mood in default_themes:
                    all_themes.extend(default_themes[mood])
        
        return list(set(all_themes)) if all_themes else ['patience', 'kindness']
    
    def find_matching_hadith(self, themes: list) -> list:
        """Find hadith that match the relevant themes"""
        matching_hadith = []
        
        for theme in themes:
            hadith_list = self.db.query(Hadith).filter(
                Hadith.theme.ilike(f"%{theme}%")
            ).all()
            matching_hadith.extend(hadith_list)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_hadith = []
        for hadith in matching_hadith:
            if hadith.id not in seen:
                seen.add(hadith.id)
                unique_hadith.append(hadith)
        
        return unique_hadith
    
    def select_best_hadith(self, hadith_list: list, mood_keywords: list) -> object:
        """Select the most appropriate hadith for the mood"""
        if not hadith_list:
            # Fallback to any hadith
            return self.db.query(Hadith).first()
        
        # Prioritize based on mood - for now, random selection
        # In a more advanced version, we could rank by relevance
        return random.choice(hadith_list)
    
    def format_mood_response(self, hadith: object, original_mood: str, mood_keywords: list) -> dict:
        """Format the response for mood-based request"""
        return {
            'mood_detected': ', '.join(mood_keywords) if mood_keywords != ['general'] else 'seeking guidance',
            'hadith': {
                'text': hadith.text_english,
                'arabic': hadith.text_arabic or '',
                'source': f"{hadith.collection}, Book: {hadith.book}, Hadith #{hadith.hadith_number}",
                'grade': hadith.grade,
                'theme': hadith.theme,
                'narrator': hadith.narrator
            },
            'relevance_explanation': self.generate_relevance_explanation(hadith, mood_keywords),
            'personal_reflection': self.generate_reflection_question(hadith, mood_keywords)
        }
    
    def generate_relevance_explanation(self, hadith: object, mood_keywords: list) -> str:
        """Generate explanation of why this hadith is relevant to the mood"""
        explanations = {
            'sad': f"This hadith about {hadith.theme} offers comfort and perspective during difficult times.",
            'angry': f"This hadith about {hadith.theme} provides guidance on managing difficult emotions with wisdom.",
            'worried': f"This hadith about {hadith.theme} reminds us to trust in divine wisdom and find peace.",
            'lazy': f"This hadith about {hadith.theme} motivates us to take positive action and find purpose.",
            'grateful': f"This hadith about {hadith.theme} deepens our appreciation and thankfulness.",
            'lonely': f"This hadith about {hadith.theme} reminds us of our connection to others and to Allah.",
            'confused': f"This hadith about {hadith.theme} provides clarity and direction.",
            'hopeless': f"This hadith about {hadith.theme} offers hope and reminds us of Allah's mercy."
        }
        
        for mood in mood_keywords:
            if mood in explanations:
                return explanations[mood]
        
        return f"This hadith about {hadith.theme} provides wisdom and guidance for your current situation."
    
    def generate_reflection_question(self, hadith: object, mood_keywords: list) -> str:
        """Generate a personal reflection question"""
        questions = {
            'sad': "How might this hadith bring comfort and hope to your heart today?",
            'angry': "What steps can you take to apply this hadith's wisdom in managing your emotions?",
            'worried': "How can you use this hadith to find peace and trust in Allah's plan?",
            'lazy': "What small action can you take today that aligns with this hadith's message?",
            'grateful': "How does this hadith inspire you to express gratitude in your daily life?",
            'lonely': "How might this hadith help you feel more connected to your community?",
            'confused': "What clarity does this hadith offer for your current situation?",
            'hopeless': "How does this hadith remind you of the hope and mercy available to you?"
        }
        
        for mood in mood_keywords:
            if mood in questions:
                return questions[mood]
        
        return "How can you apply this hadith's wisdom to bring positive change to your life?"

@router.post("/mood", response_model=dict)
def find_mood_hadith(
    request: MoodRequest,
    db: Session = Depends(get_db)
):
    """
    Find a relevant hadith based on user's mood or feeling
    
    - **mood**: Description of how you're feeling (e.g., "I'm sad today", "feeling angry", "grateful")
    """
    mood_text = request.mood.strip()
    
    if not mood_text:
        raise HTTPException(status_code=400, detail="Mood description is required")
    
    if len(mood_text) > 500:
        raise HTTPException(status_code=400, detail="Mood description too long (max 500 characters)")
    
    try:
        matcher = MoodHadithMatcher(db)
        result = matcher.find_hadith_for_mood(mood_text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding hadith: {str(e)}")

@router.get("/mood/test")
def test_mood_endpoint():
    """Test endpoint to verify the mood API is working"""
    return {
        "message": "Mood API is working!",
        "example_usage": {
            "endpoint": "/api/v1/mood",
            "method": "POST",
            "body": {"mood": "I'm feeling sad today"},
            "response": "Returns relevant hadith for your mood"
        }
    }