from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Hadith
from rapidfuzz import fuzz

router = APIRouter()

@router.get("/search")
def search_hadith(query: str = Query(..., min_length=3), db: Session = Depends(get_db)):
    """
    Search hadiths by partial sentence (English or Arabic).
    Uses fuzzy matching to handle fragments.
    """
    # Get all hadiths (could paginate later)
    all_hadiths = db.query(Hadith).all()

    results = []
    for hadith in all_hadiths:
        score_en = fuzz.partial_ratio(query.lower(), (hadith.text_en or "").lower())
        score_ar = fuzz.partial_ratio(query, hadith.text_ar or "")

        if score_en > 70 or score_ar > 70:  # adjust threshold
            results.append({
                "id": hadith.id,
                "book": hadith.book,
                "number": hadith.hadith_number,
                "text_en": hadith.text_en[:200] + "..." if len(hadith.text_en) > 200 else hadith.text_en,
                "text_ar": hadith.text_ar[:200] + "..." if len(hadith.text_ar) > 200 else hadith.text_ar,
                "authenticity": "Sahih al-Bukhari",
                "match_score": max(score_en, score_ar)
            })

    # Sort by best match
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    return results
