from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User, Role, Gender, LoginType
from schemas.user import UserCreate, UserUpdate, UserOAuthCreate
from utils.auth import get_password_hash, verify_password, create_access_token
from typing import Optional, List
from sqlalchemy import desc
from utils.email_utils import send_email
from services.redis_manager import redis_manager
import random
import datetime
from fastapi import BackgroundTasks

class AuthService:

    @staticmethod
    def _parse_role(role_str: str | None) -> int:
        if not role_str:
            return Role.STUDENT.value
        try:
            return Role[role_str.upper()].value
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )

    @staticmethod
    def _parse_gender(gender_str: str | None) -> Gender:
        if not gender_str:
            return Gender.OTHER
        try:
            return Gender(gender_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid gender"
            )

    @staticmethod
    def _parse_login_type(login_type_str: str | None) -> LoginType:
        if not login_type_str:
            return LoginType.DEFAULT
        try:
            return LoginType(login_type_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid login type"
            )

    @staticmethod
    def register_user(user: UserCreate, db: Session):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        role_value = AuthService._parse_role(user.role)
        gender_enum = AuthService._parse_gender(user.gender)
        login_type_enum = AuthService._parse_login_type(user.login_type)

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=role_value,
            full_name=user.full_name,
            age=user.age,
            class_name=user.class_name,
            gender=gender_enum,
            login_type=login_type_enum,
            oauth_id=user.oauth_id,
            verified=user.verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": Role(role_value).name,
                "login_type": login_type_enum.value
            }
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "login_type": login_type_enum.value
        }

    @staticmethod
    async def request_otp(email: str, background_tasks: BackgroundTasks):

        subject = "Đăng ký tài khoản thành công"
        body = f"""
         <html>
            <body>
                <p>Xin chào,</p>
                <p>Chúc mừng bạn đã đăng ký tài khoản thành công!</p>
                <p>Email của bạn: <strong>{email}</strong></p>
                <p>Bạn có thể bắt đầu sử dụng hệ thống ngay bây giờ.</p>
                <p>Trân trọng,</p>
                <p>Đội ngũ hỗ trợ</p>
            </body>
        </html>
        """
        background_tasks.add_task(send_email, subject, email, body)
        return {"message": "Email thông báo đăng ký thành công đã được gửi đến email của bạn."}

    @staticmethod
    async def verify_otp(email: str, otp: str, db: Session):
        otp_key = f"otp:{email}"
        stored_otp = await redis_manager.get(otp_key)

        if not stored_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã OTP không hợp lệ hoặc đã hết hạn."
            )

        if stored_otp != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã OTP không chính xác."
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.verified = True
        db.commit()

        await redis_manager.delete(otp_key)  # Invalidate OTP after successful verification
        return {"message": "Xác thực OTP thành công."}

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user or not verify_password(password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        role_name = Role(db_user.role).name if isinstance(db_user.role, int) else str(db_user.role)
        access_token = create_access_token(
            data={
                "sub": email,
                "role": role_name,
                "login_type": db_user.login_type.value
            }
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "login_type": db_user.login_type.value
        }

    @staticmethod
    def get_users(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        email: Optional[str] = None,
        gender: Optional[str] = None,
        role: Optional[str] = None,
        login_type: Optional[str] = None,
        class_names: Optional[List[str]] = None,
    ):
        query = db.query(User)

        if email:
            query = query.filter(User.email.ilike(f"%{email}%"))

        if gender:
            try:
                gender_enum = Gender(gender.lower())
                query = query.filter(User.gender == gender_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid gender"
                )

        if role:
            try:
                role_value = Role[role.upper()].value
                query = query.filter(User.role == role_value)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role"
                )

        if login_type:
            try:
                login_type_enum = LoginType(login_type.lower())
                query = query.filter(User.login_type == login_type_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid login type"
                )

        if class_names:
            query = query.filter(User.class_name.in_(class_names))

        query = query.order_by(desc(User.id))
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        return users

    @staticmethod
    def create_user(user: UserCreate, db: Session):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        role_value = AuthService._parse_role(user.role)
        gender_enum = AuthService._parse_gender(user.gender)
        login_type_enum = AuthService._parse_login_type(user.login_type)

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            role=role_value,
            full_name=user.full_name,
            age=user.age,
            class_name=user.class_name,
            gender=gender_enum,
            login_type=login_type_enum,
            oauth_id=user.oauth_id,
            verified=user.verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def create_oauth_user(user: UserOAuthCreate, db: Session):
        existing_user = db.query(User).filter(User.email == user.email).first()

        if existing_user:
            existing_user.login_type = AuthService._parse_login_type(user.login_type)
            existing_user.oauth_id = user.oauth_id
            if user.full_name:
                existing_user.full_name = user.full_name
            db.commit()
            db.refresh(existing_user)
            return existing_user

        db_user = User(
            email=user.email,
            hashed_password="oauth_user",
            role=Role.STUDENT.value,
            full_name=user.full_name,
            gender=AuthService._parse_gender(user.gender),
            login_type=AuthService._parse_login_type(user.login_type),
            oauth_id=user.oauth_id,
            verified=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(user_id: int, user_update: UserUpdate, db: Session):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user_update.email:
            if db.query(User).filter(User.email == user_update.email, User.id != user_id).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            db_user.email = user_update.email

        if user_update.password:
            db_user.hashed_password = get_password_hash(user_update.password)

        if user_update.role:
            db_user.role = AuthService._parse_role(user_update.role)

        if user_update.gender:
            db_user.gender = AuthService._parse_gender(user_update.gender)

        if user_update.login_type:
            db_user.login_type = AuthService._parse_login_type(user_update.login_type)

        if user_update.oauth_id:
            db_user.oauth_id = user_update.oauth_id

        if user_update.full_name:
            db_user.full_name = user_update.full_name

        if user_update.age is not None:
            db_user.age = user_update.age

        if user_update.class_name:
            db_user.class_name = user_update.class_name

        if user_update.verified is not None:
            db_user.verified = user_update.verified

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(user_id: int, db: Session):
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        db.delete(db_user)
        db.commit()
        return {"detail": "User deleted successfully"}
