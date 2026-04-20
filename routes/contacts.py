from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Contact

router = APIRouter()

def get_db():
    db = SessionLocal()
    yield db

@router.get("/")
def get_contacts(user_id: int, db: Session = Depends(get_db)):
    return db.query(Contact).filter(Contact.user_id == user_id).all()