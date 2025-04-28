# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # <- AICI este modificarea importantă

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # Acum este corect și compatibil cu SQLAlchemy 2.x

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
