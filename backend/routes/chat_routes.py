import uuid
from fastapi import APIRouter, HTTPException, status, Depends

from schemas.chat import ChatRequest, ChatResponse
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_response(
    request: ChatRequest, 
    current_user: dict = Depends(get_current_user)
) -> ChatResponse:
    # User is authenticated - current_user contains {"email": "...", "role": "..."}
    return ChatResponse(
        response=f"Hello {current_user['email']}, how can I help you today?",
        session_id=request.session_id or str(uuid.uuid4())
    )