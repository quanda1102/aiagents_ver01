from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class Role(PyEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(SqlEnum(Role, values_callable=lambda x: [e.value for e in x]), default=Role.STUDENT.value)
    full_name = Column(String(255))
    age = Column(Integer, nullable=True)
