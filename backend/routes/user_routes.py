from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from config import config
from models.user import Base, Role, User
from schemas.user import UserCreate, UserUpdate, UserOut
from services.auth_service import AuthService
from utils.auth import get_current_user

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(current_user: User = Depends(get_current_user)):
    # Convert role integer to role name for comparison
    from models.user import Role
    user_role_name = Role(current_user.role).name if isinstance(current_user.role, int) else str(current_user.role)
    if user_role_name != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = AuthService.get_users(db)
    return [UserOut.from_orm_with_role_name(u) for u in users]

@router.post("/", response_model=UserOut)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    new_user = AuthService.create_user(user, db)
    return UserOut.from_orm_with_role_name(new_user)

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_user = AuthService.update_user(user_id, user, db)
    return UserOut.from_orm_with_role_name(updated_user)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return AuthService.delete_user(user_id, db)
