import models

def create_contact(db, contact, user_id):
    new_contact = models.Contact(**contact.dict(), user_id=user_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_contacts(db, user_id):
    return db.query(models.Contact).filter_by(user_id=user_id).all()