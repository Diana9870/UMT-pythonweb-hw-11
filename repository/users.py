from sqlalchemy.orm import Session
from models.user import User

async def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

async def create_user(db: Session, email: str, password: str):
    user = User(email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user