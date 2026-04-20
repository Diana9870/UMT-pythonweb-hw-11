from sqlalchemy import Column, Integer, String, Boolean
from conf.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)