from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config import config
from models.user import User
from database import get_db
import time
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    start_time = time.time()
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        end_time = time.time()
        logger.info(f"[AUTH_UTILS] verify_password completed in {end_time - start_time:.4f} seconds")
        return result
    except Exception as e:
        end_time = time.time()
        logger.error(f"[AUTH_UTILS] verify_password failed after {end_time - start_time:.4f} seconds with error: {str(e)}")
        raise

def get_password_hash(password):
    start_time = time.time()
    try:
        result = pwd_context.hash(password)
        end_time = time.time()
        logger.info(f"[AUTH_UTILS] get_password_hash completed in {end_time - start_time:.4f} seconds")
        return result
    except Exception as e:
        end_time = time.time()
        logger.error(f"[AUTH_UTILS] get_password_hash failed after {end_time - start_time:.4f} seconds with error: {str(e)}")
        raise

def create_access_token(data: dict, expires_delta: timedelta = None):
    start_time = time.time()
    try:
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
        end_time = time.time()
        logger.info(f"[AUTH_UTILS] create_access_token completed in {end_time - start_time:.4f} seconds")
        return encoded_jwt
    except Exception as e:
        end_time = time.time()
        logger.error(f"[AUTH_UTILS] create_access_token failed after {end_time - start_time:.4f} seconds with error: {str(e)}")
        raise

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    start_time = time.time()
    logger.info(f"[AUTH_UTILS] get_current_user started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Decode JWT token
        jwt_decode_start = time.time()
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")  # sub bây giờ là email
        jwt_decode_end = time.time()
        logger.info(f"[AUTH_UTILS] JWT token decoding completed in {jwt_decode_end - jwt_decode_start:.4f} seconds")

        print("JWT Payload:", payload)

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Token thiếu thông tin người dùng (sub)"
            )

        # Step 2: Query user from database
        db_query_start = time.time()
        user = db.query(User).filter(User.email == email).first()
        db_query_end = time.time()
        logger.info(f"[AUTH_UTILS] Database user query completed in {db_query_end - db_query_start:.4f} seconds")

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy người dùng với email: {email}"
            )

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"[AUTH_UTILS] get_current_user completed successfully in {execution_time:.4f} seconds")
        return user

    except jwt.ExpiredSignatureError:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"[AUTH_UTILS] get_current_user failed after {execution_time:.4f} seconds: Token expired")
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"[AUTH_UTILS] get_current_user failed after {execution_time:.4f} seconds: Invalid token - {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token không hợp lệ: {str(e)}")
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"[AUTH_UTILS] get_current_user failed after {execution_time:.4f} seconds with error: {str(e)}")
        raise
