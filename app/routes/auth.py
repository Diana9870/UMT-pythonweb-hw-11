from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.conf.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

from app.services.auth import auth_service
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    hashed_password = auth_service.get_password_hash(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth_service.create_email_token({"sub": new_user.email})

    background_tasks.add_task(
        send_verification_email,
        new_user.email,
        token,
    )

    return new_user


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == data.email).first()

    if user is None or not auth_service.verify_password(
        data.password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )

    access_token = auth_service.create_access_token(
        {"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    try:
        email = auth_service.get_email_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"message": "Email successfully verified"}


@router.post("/request-email")
async def request_email_verification(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return {"message": "Email already verified"}

    token = auth_service.create_email_token({"sub": user.email})

    background_tasks.add_task(
        send_verification_email,
        user.email,
        token,
    )

    return {"message": "Verification email sent"}

