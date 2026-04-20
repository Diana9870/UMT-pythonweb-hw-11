from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.services.auth import *
from app.services.email import send_verification_email

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=201)
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=409, detail="User exists")

    new_user = User(
        email=email,
        password=hash_password(password)
    )
    db.add(new_user)
    db.commit()

    token = create_email_token(email)
    send_verification_email(email, token)

    return new_user


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token = create_access_token({"sub": user.email})
    return {"access_token": token}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    data = decode_token(token)
    user = db.query(User).filter(User.email == data["sub"]).first()

    user.is_verified = True
    db.commit()

    return {"message": "Email verified"}