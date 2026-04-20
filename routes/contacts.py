from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.deps import get_current_user
from src.conf.db import get_db
from src.schemas.contact import ContactCreate
from src.repository.contacts import create_contact, get_contacts

router = APIRouter(prefix="/api/contacts")

@router.post("/", status_code=201)
async def create(data: ContactCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return await create_contact(db, data, user.id)


@router.get("/")
async def all(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return await get_contacts(db, user.id)