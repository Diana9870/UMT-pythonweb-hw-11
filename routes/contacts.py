from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Contact

router = APIRouter()

def get_db():
    db = SessionLocal()
    yield db

def get_contacts(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Contact).filter(Contact.user_id == user.id).all()