from sqlalchemy.orm import Session
from src.models.contact import Contact

async def create_contact(db: Session, data, user_id):
    contact = Contact(**data.dict(), user_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contacts(db: Session, user_id):
    return db.query(Contact).filter(Contact.user_id == user_id).all()