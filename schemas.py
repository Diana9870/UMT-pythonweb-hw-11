from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str


class ContactResponse(ContactCreate):
    id: int

    class Config:
        from_attributes = True