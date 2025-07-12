from pydantic import BaseModel, EmailStr

class ChatRequest(BaseModel):
    user_id: int
    user_name: str
    user_email: EmailStr
    user_phone: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str
    user_country: str 
    user_role: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str