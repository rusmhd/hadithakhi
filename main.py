from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.api import mood

app = FastAPI(title="Hadithaki API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class HadithRequest(BaseModel):
    text: str

# Routes
@app.get("/")
def root():
    return {"message": "Hadithaki API is running! 🚀"}

app.include_router(search.router, prefix="/api", tags=["search"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/verify")
def verify_hadith(request: HadithRequest):
    hadith_text = request.text
    if "Actions are but by intention" in hadith_text:
        return {"result": "✅ Authentic - Sahih Bukhari, Book 1, Hadith 1"}
    else:
        return {"result": "❌ Could not verify authenticity"}

# Include mood API
app.include_router(mood.router, prefix="/api/v1", tags=["mood"])


from fastapi import FastAPI
from app.api import search

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hadithaki API is running! 🚀"}

app.include_router(search.router, prefix="/api", tags=["Search"])
