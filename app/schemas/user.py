from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_verified: bool
    avatar: Optional[str] = None

    class Config:
        from_attributes = True 


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdateAvatar(BaseModel):
    avatar: str