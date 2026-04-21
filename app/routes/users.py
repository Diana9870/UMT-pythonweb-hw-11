from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.conf.db import get_db
from app.services.cloudinary_service import upload_avatar
from app.models import User

from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)


@router.get("/me")
@limiter.limit("5/minute")
async def get_current_user_info(
    request: Request, 
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch("/avatar", status_code=status.HTTP_200_OK)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    avatar_url = await upload_avatar(file, current_user.id)

    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)

    return {"avatar": avatar_url}