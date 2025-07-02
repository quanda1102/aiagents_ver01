from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from typing import List, Dict, Any

conversation_store: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

class ConversationHistoryService:
    @staticmethod
    def save_turn(session_id: str, turn_data: Dict[str, Any]) -> None:
        """
        Lưu một lượt hội thoại vào session tương ứng.
        """
        conversation = conversation_store[session_id]
        conversation.append({
            **turn_data,
            "turnId": len(conversation) + 1,
            "timestamp": datetime.utcnow().isoformat(),
        })

    @staticmethod
    def get_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lấy các lượt hội thoại gần nhất.
        """
        return conversation_store[session_id][-limit:]

    @staticmethod
    def get_all_sessions() -> List[str]:
        """
        Trả về danh sách sessionId đã ghi nhận.
        """
        return list(conversation_store.keys())
