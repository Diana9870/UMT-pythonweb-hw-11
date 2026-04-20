from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.deps import get_current_user
from src.conf.db import get_db
from src.services.cloudinary_service import upload_avatar

router = APIRouter(prefix="/api/users")

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user


@router.patch("/avatar")
async def avatar(file: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    url = await upload_avatar(file, user.id)
    user.avatar = url
    db.commit()
    return {"avatar": url}