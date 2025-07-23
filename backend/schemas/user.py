from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
from models.user import Role, Gender, LoginType

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    role: Optional[str] = None
    class_name: Optional[List[str]] = None
    gender: Optional[str] = "other"
    login_type: Optional[str] = "default"
    oauth_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "full_name": "John Doe",
                "age": 25,
                "role": "STUDENT",
                "gender": "male",
                "login_type": "default"
            }
        }

class UserOAuthCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    login_type: str = Field(..., pattern="^(google|facebook)$")
    oauth_id: str
    role: Optional[str] = None
    gender: Optional[str] = "other"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    login_type: Optional[str] = "default"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    full_name: Optional[str]
    age: Optional[int]
    class_name: Optional[List[str]]
    gender: Optional[str]
    login_type: Optional[str]
    oauth_id: Optional[str]

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

        # Handle login_type
        try:
            login_type = user.login_type.value if hasattr(user.login_type, 'value') else str(user.login_type)
        except Exception:
            login_type = "default"

        # Handle class_name
        class_name = []
        if user.class_name is not None:
            if isinstance(user.class_name, list):
                class_name = user.class_name
            else:
                class_name = [str(user.class_name)]
        
        return UserOut(
            id=user.id,
            email=user.email,
            role=role_name,
            full_name=user.full_name,
            age=user.age,
            class_name=class_name,
            gender=gender_value,
            login_type=login_type,
            oauth_id=user.oauth_id
        )

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    class_name: Optional[List[str]] = None
    gender: Optional[str] = None
    login_type: Optional[str] = None
    oauth_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    login_type: Optional[str] = None

class ClassUpdate(BaseModel):
    class_name: List[str]

class OAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    login_type: str
    email: EmailStr
    is_new_user: bool