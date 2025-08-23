from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from config import config
from models.user import Base, Role, User, LoginType
from schemas.user import UserCreate, UserUpdate, UserOut, UserOAuthCreate
from services.auth_service import AuthService
from utils.auth import get_current_user
from database import engine, SessionLocal
from sqlalchemy import desc

router = APIRouter(prefix="/api/v1/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(current_user: User = Depends(get_current_user)):
    try:
        user_role_name = Role(current_user.role).name if isinstance(current_user.role, int) else str(current_user.role)
        if user_role_name != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )

@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    email: Optional[str] = None,
    gender: Optional[str] = None,
    role: Optional[str] = None,
    login_type: Optional[str] = None,
    class_names: Optional[List[str]] = Query(None)
):
    """
    Get all users with filtering options (Admin only)
    """
    try:
        # Validate login_type if provided
        if login_type and login_type not in [t.value for t in LoginType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid login_type. Must be one of: {[t.value for t in LoginType]}"
            )

        users = AuthService.get_users(
            db,
            page=page,
            page_size=page_size,
            email=email,
            gender=gender,
            role=role,
            login_type=login_type,
            class_names=class_names
        )
        return [UserOut.from_orm_with_role_name(u) for u in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", response_model=UserOut)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create new user (Admin only)
    """
    try:
        new_user = AuthService.create_user(user, db)
        return UserOut.from_orm_with_role_name(new_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/oauth", response_model=UserOut)
def create_oauth_user(
    user: UserOAuthCreate,
    db: Session = Depends(get_db)
):
    """
    Create new user from OAuth provider
    """
    try:
        new_user = AuthService.create_oauth_user(user, db)
        return UserOut.from_orm_with_role_name(new_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create OAuth user"
        )

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update user (Admin only)
    """
    try:
        updated_user = AuthService.update_user(user_id, user, db)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserOut.from_orm_with_role_name(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user (Admin only)
    """
    try:
        success = AuthService.delete_user(user_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )