from fastapi import APIRouter, Query, HTTPException
from my_agents.services.conversation_history_service import ConversationHistoryService

router = APIRouter()

@router.get("/history")
def get_history(sessionId: str = Query(None), limit: int = Query(10)):
    if not sessionId:
        raise HTTPException(status_code=400, detail="Thiếu sessionId")
    
    history = ConversationHistoryService.get_history(sessionId, limit)
    return {
        "success": True,
        "sessionId": sessionId,
        "history": history,
    }

@router.get("/sessions")
def get_all_sessions():
    sessions = ConversationHistoryService.get_all_sessions()
    return {
        "success": True,
        "sessions": sessions,
    }
