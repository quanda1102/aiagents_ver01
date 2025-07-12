import uuid
from fastapi import APIRouter, HTTPException, status

from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_response(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        response="Hello, how can I help you today?",
        session_id=request.session_id or str(uuid.uuid4())
    )