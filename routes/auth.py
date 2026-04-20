from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from src.conf.db import get_db
from src.schemas.user import UserCreate
from src.repository.users import get_user_by_email, create_user
from src.services.auth import hash_password, verify_password, create_access_token, create_email_token, decode_token
from src.services.email import send_verification_email

router = APIRouter(prefix="/api/auth")

@router.post("/register", status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if await get_user_by_email(db, user.email):
        raise HTTPException(409)

    hashed = hash_password(user.password)
    new_user = await create_user(db, user.email, hashed)

    token = create_email_token({"sub": user.email})
    await send_verification_email(user.email, token)

    return new_user


@router.get("/verify")
async def verify(token: str, db: Session = Depends(get_db)):
    data = decode_token(token)
    user = await get_user_by_email(db, data["sub"])
    user.is_verified = True
    db.commit()
    return {"message": "verified"}


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await get_user_by_email(db, form.username)

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401)

    if not user.is_verified:
        raise HTTPException(403)

    token = create_access_token({"sub": user.email})
    return {"access_token": token}