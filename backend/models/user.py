from sqlalchemy import Column, Integer, String, Enum as SqlEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from models import Base

class Role(PyEnum):
    ADMIN = 8686
    TEACHER = 2
    STUDENT = 3

class Gender(PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

# Thêm enum cho login_type
class LoginType(PyEnum):
    DEFAULT = "default"
    GOOGLE = "google"
    FACEBOOK = "facebook"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(Integer, default=Role.STUDENT.value)
    full_name = Column(String(255))
    age = Column(Integer, nullable=True)
    class_name = Column(JSON, default=[])
    gender = Column(SqlEnum(Gender, values_callable=lambda x: [e.value for e in x]), default=Gender.OTHER.value)
    
    # Thêm 2 trường mới
    login_type = Column(
        SqlEnum(LoginType, values_callable=lambda x: [e.value for e in x]),
        default=LoginType.DEFAULT.value
    )
    oauth_id = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    
    # Các relationship
    lectures = relationship("Lecture", back_populates="teacher")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")