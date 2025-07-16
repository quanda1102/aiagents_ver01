from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from config import config
from models.user import Base
from schemas.user import UserCreate, UserLogin, Token
from services.auth_service import AuthService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.auth import get_current_user
from models.user import User
from schemas.user import ClassUpdate
from schemas.user import UserOut
from typing import List

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

@router.get("/me", response_model=UserOut)
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm_with_role_name(current_user)

class UpdateClassName(BaseModel):
    class_name: List[str]

@router.put("/me/class-name")
async def update_class_name(
    update: UpdateClassName,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.class_name = update.class_name
    db.commit()
    return {"message": "Class names updated successfully"}
