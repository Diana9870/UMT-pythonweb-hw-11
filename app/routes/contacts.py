from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.conf.db import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_contact = Contact(**contact.model_dump())
    new_contact.user_id = user.id

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contacts = (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .all()
    )

    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user.id,
        )
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user.id,
        )
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    for field, value in contact_data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user.id,
        )
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    db.delete(contact)
    db.commit()

    return None
