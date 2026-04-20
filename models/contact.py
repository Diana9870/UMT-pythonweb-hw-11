from sqlalchemy import Column, Integer, String, ForeignKey
from src.conf.db import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))