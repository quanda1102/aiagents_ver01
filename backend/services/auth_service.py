from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import User, Role, Gender
from schemas.user import UserCreate, UserUpdate
from utils.auth import get_password_hash, verify_password, create_access_token

class AuthService:

    @staticmethod
    def _parse_role(role_str: str | None) -> int:
        """Chuyển đổi role từ chuỗi sang Enum value"""
        if not role_str:
            return Role.STUDENT.value
        try:
            return Role[role_str.upper()].value
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid role")

    @staticmethod
    def _parse_gender(gender_str: str | None) -> Gender:
        """Chuyển đổi gender từ chuỗi sang Enum"""
        if not gender_str:
            return Gender.OTHER
        try:
            return Gender(gender_str.lower())
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid gender")

    @staticmethod
    def register_user(user: UserCreate, db: Session):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        role_value = AuthService._parse_role(user.role)
        gender_enum = AuthService._parse_gender(user.gender)

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=role_value,
            full_name=user.full_name,
            age=user.age,
            class_name=user.class_name,
            gender=gender_enum
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        access_token = create_access_token(data={"sub": user.email, "role": Role(role_value).name})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user or not verify_password(password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        role_name = Role(db_user.role).name if isinstance(db_user.role, int) else str(db_user.role)
        access_token = create_access_token(data={"sub": email, "role": role_name})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def get_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def create_user(user: UserCreate, db: Session):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        role_value = AuthService._parse_role(user.role)
        gender_enum = AuthService._parse_gender(user.gender)

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=role_value,
            full_name=user.full_name,
            age=user.age,
            class_name=user.class_name,
            gender=gender_enum
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(user_id: int, user_update: UserUpdate, db: Session):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_update.email:
            if db.query(User).filter(User.email == user_update.email, User.id != user_id).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            db_user.email = user_update.email

        if user_update.password:
            db_user.hashed_password = get_password_hash(user_update.password)

        if user_update.role:
            db_user.role = AuthService._parse_role(user_update.role)

        if user_update.gender:
            db_user.gender = AuthService._parse_gender(user_update.gender)

        if user_update.full_name:
            db_user.full_name = user_update.full_name

        if user_update.age is not None:
            db_user.age = user_update.age

        if user_update.class_name:
            db_user.class_name = user_update.class_name

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(user_id: int, db: Session):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(db_user)
        db.commit()
        return {"detail": "User deleted successfully"}
