from sqlalchemy import Column, Integer, String, Enum as SqlEnum, JSON
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from models import Base  # sửa lại dòng này

class Role(PyEnum):
    ADMIN = 8686
    TEACHER = 2
    STUDENT = 3

class Gender(PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Integer, default=Role.STUDENT.value)
    full_name = Column(String(255))
    age = Column(Integer, nullable=True)
    class_name = Column(JSON, default=[])
    gender = Column(SqlEnum(Gender, values_callable=lambda x: [e.value for e in x]), default=Gender.OTHER.value)
    lectures = relationship("Lecture", back_populates="teacher")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
