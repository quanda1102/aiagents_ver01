from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import config
from models.user import Base
from schemas.user import UserCreate, UserLogin, Token
from services.auth_service import AuthService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.auth import get_current_user

# Kết nối CSDL
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo bảng
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(user, db)

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(user.email, user.password, db)

@router.get("/me")
def get_logged_in_user(current_user: dict = Depends(get_current_user)):
    return current_user
