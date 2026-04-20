from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from deps import get_current_user
from conf.db import get_db
from services.cloudinary_service import upload_avatar

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/me")
@limiter.limit("5/minute")
async def me(user=Depends(get_current_user)):
    return user

router = APIRouter(prefix="/api/users")

@router.patch("/avatar")
async def avatar(file: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    url = await upload_avatar(file, user.id)
    user.avatar = url
    db.commit()
    return {"avatar": url}