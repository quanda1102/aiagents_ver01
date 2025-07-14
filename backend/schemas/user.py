from pydantic import BaseModel, EmailStr
from typing import Optional
from models.user import Role, Gender
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = "other"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    full_name: Optional[str]
    age: Optional[int]
    class_name: Optional[str]
    gender: Optional[str]

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm_with_role_name(user):
        return UserOut(
            id=user.id,
            email=user.email,
            role=Role(user.role).name if isinstance(user.role, int) else str(user.role),
            full_name=user.full_name,
            age=user.age,
            class_name=user.class_name,
            gender=user.gender.value if isinstance(user.gender, Gender) else str(user.gender)
        )

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class ClassUpdate(BaseModel):
    class_name: str