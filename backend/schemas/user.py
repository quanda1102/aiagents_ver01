from pydantic import BaseModel, EmailStr
from typing import Optional

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
    role: int
    full_name: Optional[str]
    age: Optional[int]
    class_name: Optional[str]
    gender: Optional[str]

    model_config = {"from_attributes": True}

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
