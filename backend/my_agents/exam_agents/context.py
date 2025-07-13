"""
Context Manager for Multi-Agent Exam Generation System
Handles context sharing, state management, and Redis storage
"""
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from services.redis_manager import get_redis_client
import logging

logger = logging.getLogger(__name__)


class ExamContextManager:
    """
    Manages context and state for multi-agent exam generation workflow
    """
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.context_prefix = "exam_context:"
        self.session_prefix = "exam_session:"
        self.agent_state_prefix = "agent_state:"
        self.default_ttl = 3600  # 1 hour
    
    def create_session(self, user_id: str, exam_request: Dict[str, Any]) -> str:
        """Create a new exam generation session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "initialized",
            "current_agent": "ExamManagerAgent",
            "exam_request": exam_request,
            "workflow_state": {
                "format_completed": False,
                "questions_generated": False,
                "editing_completed": False
            },
            "results": {
                "format_spec": None,
                "questions": [],
                "quality_assessment": None,
                "final_exam": None
            }
        }
        
        # Store session data
        self._store_session_data(session_id, session_data)
        
        logger.info(f"Created exam generation session: {session_id}")
        return session_id
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            if not self.redis_client:
                return None
            
            key = f"{self.session_prefix}{session_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving session data: {e}")
            return None
    
    def update_session_data(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_data = self.get_session_data(session_id)
            if not session_data:
                return False
            
            # Deep merge updates
            session_data.update(updates)
            session_data["updated_at"] = datetime.utcnow().isoformat()
            
            return self._store_session_data(session_id, session_data)
            
        except Exception as e:
            logger.error(f"Error updating session data: {e}")
            return False
    
    def set_current_agent(self, session_id: str, agent_name: str) -> bool:
        """Set the current active agent"""
        return self.update_session_data(session_id, {"current_agent": agent_name})
    
    def get_current_agent(self, session_id: str) -> Optional[str]:
        """Get the current active agent"""
        session_data = self.get_session_data(session_id)
        if session_data:
            return session_data.get("current_agent")
        return None
    
    def store_agent_result(self, session_id: str, agent_name: str, result: Dict[str, Any]) -> bool:
        """Store result from a specific agent"""
        try:
            session_data = self.get_session_data(session_id)
            if not session_data:
                return False
            
            # Store agent-specific result
            if agent_name == "ExamFormatAgent":
                session_data["results"]["format_spec"] = result
                session_data["workflow_state"]["format_completed"] = True
            elif agent_name == "QuestionGeneratorAgent":
                session_data["results"]["questions"] = result
                session_data["workflow_state"]["questions_generated"] = True
            elif agent_name == "ExamEditorAgent":
                session_data["results"]["quality_assessment"] = result
                session_data["workflow_state"]["editing_completed"] = True
            
            # Update overall status
            workflow_state = session_data["workflow_state"]
            if all(workflow_state.values()):
                session_data["status"] = "completed"
            else:
                session_data["status"] = "in_progress"
            
            return self._store_session_data(session_id, session_data)
            
        except Exception as e:
            logger.error(f"Error storing agent result: {e}")
            return False
    
    def get_context_for_agent(self, session_id: str, agent_name: str) -> Dict[str, Any]:
        """Get context relevant for a specific agent"""
        session_data = self.get_session_data(session_id)
        if not session_data:
            return {}
        
        base_context = {
            "session_id": session_id,
            "agent_name": agent_name,
            "exam_request": session_data.get("exam_request", {}),
            "workflow_state": session_data.get("workflow_state", {}),
            "user_id": session_data.get("user_id", "")
        }
        
        # Add agent-specific context
        results = session_data.get("results", {})
        
        if agent_name == "ExamFormatAgent":
            # Format agent gets the original request
            base_context.update({
                "task": "create_exam_format",
                "requirements": session_data.get("exam_request", {})
            })
        
        elif agent_name == "QuestionGeneratorAgent":
            # Question generator gets format spec
            base_context.update({
                "task": "generate_questions",
                "format_spec": results.get("format_spec"),
                "requirements": session_data.get("exam_request", {})
            })
        
        elif agent_name == "ExamEditorAgent":
            # Editor gets both format and questions
            base_context.update({
                "task": "review_and_edit",
                "format_spec": results.get("format_spec"),
                "questions": results.get("questions"),
                "requirements": session_data.get("exam_request", {})
            })
        
        return base_context
    
    def get_all_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get all results from the session"""
        session_data = self.get_session_data(session_id)
        if session_data and session_data.get("status") == "completed":
            return session_data.get("results", {})
        return None
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up session data"""
        try:
            if not self.redis_client:
                return False
            
            keys_to_delete = [
                f"{self.session_prefix}{session_id}",
                f"{self.context_prefix}{session_id}",
                f"{self.agent_state_prefix}{session_id}:*"
            ]
            
            for key in keys_to_delete:
                self.redis_client.delete(key)
            
            logger.info(f"Cleaned up session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up session: {e}")
            return False
    
    def _store_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store session data in Redis"""
        try:
            if not self.redis_client:
                return False
            
            key = f"{self.session_prefix}{session_id}"
            serialized_data = json.dumps(data, default=str)
            
            self.redis_client.setex(key, self.default_ttl, serialized_data)
            return True
            
        except Exception as e:
            logger.error(f"Error storing session data: {e}")
            return False
    
    def get_session_status(self, session_id: str) -> Optional[str]:
        """Get the current status of the session"""
        session_data = self.get_session_data(session_id)
        if session_data:
            return session_data.get("status")
        return None
    
    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a user"""
        try:
            if not self.redis_client:
                return []
            
            sessions = []
            pattern = f"{self.session_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    data = self.redis_client.get(key)
                    if data:
                        session_data = json.loads(data)
                        if session_data.get("user_id") == user_id:
                            sessions.append({
                                "session_id": session_data.get("session_id"),
                                "created_at": session_data.get("created_at"),
                                "status": session_data.get("status"),
                                "current_agent": session_data.get("current_agent")
                            })
                except Exception:
                    continue
            
            # Sort by creation time, newest first
            sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing user sessions: {e}")
            return []