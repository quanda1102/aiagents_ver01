from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import User, Role
from schemas.user import UserCreate
from utils.auth import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    def register_user(user: UserCreate, db: Session):
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        if not user.role:
            user.role = Role.STUDENT.value
        elif user.role not in [r.value for r in Role]:
            raise HTTPException(status_code=400, detail="Invalid role")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
            full_name=user.full_name,
            age=user.age
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        access_token = create_access_token(data={"sub": user.email, "role": str(db_user.role)})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user or not verify_password(password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": email, "role": str(db_user.role)})
        return {"access_token": access_token, "token_type": "bearer"}
