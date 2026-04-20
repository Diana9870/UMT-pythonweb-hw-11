from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.conf.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    data.update({"exp": datetime.utcnow() + timedelta(minutes=30)})
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def create_email_token(data: dict):
    data.update({"exp": datetime.utcnow() + timedelta(hours=24)})
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])