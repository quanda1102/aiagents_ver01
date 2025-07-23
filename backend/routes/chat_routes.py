import uuid
from fastapi import APIRouter, HTTPException, status, Depends

from schemas.chat import ChatRequest, ChatResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_response(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    # User is authenticated - current_user is a User object
    # Log the received message for debugging
    print(f"📧 Chat message received from {current_user.email}: '{request.message}'")
    
    # Simple echo response with user's message for testing
    return ChatResponse(
        response=f"You said: '{request.message}'. How can I help you with that?",
        session_id=request.session_id or str(uuid.uuid4())
    )