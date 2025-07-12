from dotenv import load_dotenv
load_dotenv(override=True)
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from my_agents.config import config
import logging
from services.redis_manager import get_redis_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMemoryService:
    def __init__(self):
        """Initialize the AI Memory Service with shared Redis connection"""
        self.client = get_redis_client()
        if self.client:
            logger.info("AIMemoryService initialized with shared Redis connection")
        else:
            logger.error("AIMemoryService failed to get Redis connection")
    
    def store_message(self, user_id: str, session_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Store a single message in the conversation history"""
        if not self.client:
            logger.error("Redis client not available")
            return False
            
        try:
            redis_key = f"chat:{user_id}:{session_id}"
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # Get existing conversation or create empty list
            existing_conversation = self.get_conversation_history(user_id, session_id) or []
            existing_conversation.append(message)
            
            # Store updated conversation
            self.client.set(redis_key, json.dumps(existing_conversation))
            logger.info(f"Stored message for user {user_id}, session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, session_id: str, max_history: int = 50) -> Optional[List[Dict]]:
        """Retrieve conversation history from Redis"""
        if not self.client:
            logger.error("Redis client not available")
            return None
            
        try:
            redis_key = f"chat:{user_id}:{session_id}"
            conversation_data = self.client.get(redis_key)
            
            if conversation_data:
                conversation = json.loads(conversation_data)
                # Return the most recent messages up to max_history
                return conversation[-max_history:] if len(conversation) > max_history else conversation
            else:
                logger.info(f"No conversation history found for user {user_id}, session {session_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return None
    
    def store_user_request(self, user_request_data: Dict[str, Any]) -> bool:
        """Store a complete user request with all metadata"""
        try:
            user_id = user_request_data.get("user_id")
            session_id = user_request_data.get("session_id")
            user_message = user_request_data.get("user_message")
            
            if not all([user_id, session_id, user_message]):
                logger.error("Missing required fields: user_id, session_id, or user_message")
                return False
            
            # Store the user message
            metadata = {k: v for k, v in user_request_data.items() 
                       if k not in ["user_id", "session_id", "user_message"]}
            
            return self.store_message(user_id, session_id, "user", user_message, metadata)
            
        except Exception as e:
            logger.error(f"Error storing user request: {e}")
            return False
    
    def store_assistant_response(self, user_id: str, session_id: str, response: str, metadata: Optional[Dict] = None) -> bool:
        """Store an assistant response"""
        return self.store_message(user_id, session_id, "assistant", response, metadata)
    
    def clear_conversation(self, user_id: str, session_id: str) -> bool:
        """Clear a specific conversation"""
        if not self.client:
            logger.error("Redis client not available")
            return False
            
        try:
            redis_key = f"chat:{user_id}:{session_id}"
            self.client.delete(redis_key)
            logger.info(f"Cleared conversation for user {user_id}, session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return False
    
    def get_formatted_chat_history(self, user_id: str, session_id: str, max_history: int = 10) -> List[Dict[str, str]]:
        """Get conversation history formatted for AI model consumption"""
        conversation = self.get_conversation_history(user_id, session_id, max_history)
        
        if not conversation:
            return [{"role": "system", "content": "You are a helpful assistant."}]
        
        # Format for AI model (remove timestamp and metadata)
        formatted_history = [{"role": "system", "content": "You are a helpful assistant."}]
        
        for message in conversation:
            formatted_history.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        return formatted_history


# Example usage and testing
if __name__ == "__main__":
    # Initialize the memory service
    memory_service = AIMemoryService()
    
    # Sample user request data
    user_request_data = {
        "user_id": "1",
        "user_name": "Dang Anh Quan",
        "user_email": "dangquan@gmail.com",
        "user_phone": "0909090909",
        "user_address": "123 Nguyen Van Linh, Q9, TP.HCM",
        "user_city": "TP.HCM",
        "user_state": "Q9",
        "user_zip": "123456",
        "user_country": "Vietnam",
        "user_role": "admin",
        "session_id": "2",
        "user_message": "I want to create a new document in Google Drive"
    }
    
    # Test storing user request
    if memory_service.store_user_request(user_request_data):
        print("✅ User request stored successfully")
        print(f"User message: {user_request_data['user_message']}")
    else:
        print("❌ Failed to store user request")
    
    # Test storing assistant response
    assistant_response = "I'll help you create a new document in Google Drive. Let me access the Google Drive API for you."
    if memory_service.store_assistant_response("1", "2", assistant_response):
        print("✅ Assistant response stored successfully")
    
    # Test retrieving conversation history
    history = memory_service.get_conversation_history("1", "2")
    if history:
        print(f"✅ Retrieved {len(history)} messages from conversation history")
        for i, message in enumerate(history, 1):
            print(f"{i}. [{message['role']}]: {message['content']}")
    
    # Test getting formatted chat history for AI model
    formatted_history = memory_service.get_formatted_chat_history("1", "2")
    print(f"\n✅ Formatted chat history ready for AI model ({len(formatted_history)} messages)")

