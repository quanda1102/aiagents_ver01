from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserMetadata(BaseModel):
    user_id: int
    user_name: str
    user_role: str

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_metadata: UserMetadata


class ChatResponse(BaseModel):
    response: str
    session_id: str