from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.conf.db import get_db
from app.services.cloudinary_service import upload_avatar
from app.models import User
from app.schemas.user import UserResponse

from app.services.limiter import limiter  

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large (max 2MB)",
        )

    file.file.seek(0)

    avatar_url = await upload_avatar(file, current_user.id)

    current_user.avatar = avatar_url
    await db.commit()
    await db.refresh(current_user)

    return current_user