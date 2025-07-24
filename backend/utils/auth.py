from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config import config
from models.user import User
from database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.SECRET_KEY,
        algorithm=config.ALGORITHM
    )
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")  # sub bây giờ là email

        print("JWT Payload:", payload)

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Token thiếu thông tin người dùng (sub)"
            )

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy người dùng với email: {email}"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {str(e)}")
