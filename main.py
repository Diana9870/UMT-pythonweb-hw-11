from fastapi import FastAPI, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models, schemas, crud, auth
from deps import get_current_user

from fastapi.middleware.cors import CORSMiddleware

import cloudinary
import cloudinary.uploader
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

@app.post("/auth/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(status_code=409, detail="Email exists")

    new_user = models.User(
        email=user.email,
        password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(email=user.email).first()

    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token}

@app.get("/auth/verify/{email}")
def verify(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=email).first()
    user.is_verified = True
    db.commit()
    return {"message": "Verified"}

@app.get("/me")
@limiter.limit("5/minute")
def me(user=Depends(get_current_user)):
    return user

@app.post("/contacts", status_code=201)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.create_contact(db, contact, user.id)

@app.get("/contacts")
def get_contacts(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.get_contacts(db, user.id)

@app.post("/avatar")
def upload_avatar(
    file: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    result = cloudinary.uploader.upload(file.file)
    user.avatar = result["url"]
    db.commit()
    return {"avatar": user.avatar}