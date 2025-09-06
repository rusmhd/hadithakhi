# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Use SQLite for development
DATABASE_URL = "sqlite:///./hadithakhi.db"

# ✅ Create database engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# ✅ Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Define Base here only
Base = declarative_base()


def get_db():
    """Provide a database session (dependency for FastAPI endpoints)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
