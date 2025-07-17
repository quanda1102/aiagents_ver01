from pydantic import BaseModel, EmailStr
from typing import Optional, List
from models.user import Role, Gender

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    class_name: Optional[List[str]] = None
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
    class_name: Optional[List[str]]
    gender: Optional[str]

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm_with_role_name(user):
        try:
            role_name = Role(user.role).name if isinstance(user.role, int) else str(user.role)
        except ValueError:
            role_name = "UNKNOWN"
        
        try:
            gender_value = user.gender.value if isinstance(user.gender, Gender) else str(user.gender)
        except Exception:
            gender_value = "other"
        
        # Handle class_name - ensure it's always a list
        if user.class_name is None:
            class_name = []
        elif isinstance(user.class_name, list):
            class_name = user.class_name
        else:
            # Convert non-list values to string and wrap in list
            class_name = [str(user.class_name)]
        
        return UserOut(
            id=user.id,
            email=user.email,
            role=role_name,
            full_name=user.full_name,
            age=user.age,
            class_name=class_name,
            gender=gender_value
        )

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    class_name: Optional[List[str]] = None
    gender: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class ClassUpdate(BaseModel):
    class_name: List[str]
