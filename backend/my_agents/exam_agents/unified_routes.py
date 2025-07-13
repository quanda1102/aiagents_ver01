"""
Unified API Routes for Exam Agents
Single endpoint where agent_name parameter determines which agent to call
Uses OpenAI Agents SDK with proper context management and handoffs
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import logging

from .unified_agents import unified_agent_system, UnifiedAgentResponse
from utils.auth import get_current_user

logger = logging.getLogger(__name__)

# Create router
unified_router = APIRouter(prefix="/api/v1/exam", tags=["unified-exam-agents"])


class ChatMessage(BaseModel):
    """Message for unified agent chat"""
    message: str = Field(description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID for continuity")


@unified_router.post("/chat", response_model=UnifiedAgentResponse)
async def chat_with_agent(
    request: ChatMessage,
    agent_name: str = Query(default="triage", description="Agent to interact with: triage, format, questions, editor"),
    current_user: dict = Depends(get_current_user)
):
    """
    Unified chat endpoint for all exam agents using OpenAI Agents SDK.
    
    Workflow:
    1. Start with agent_name=triage for intelligent routing
    2. Triage routes you to appropriate specialist (format, questions, editor)
    3. Work with specialist until they complete their task and hand back to triage
    4. Triage routes to next appropriate agent based on progress
    5. Repeat until exam is complete
    
    The response.agent_name tells you which agent handled the request.
    Context and handoffs are managed automatically by the SDK.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = current_user["email"]
        
        # Validate agent name
        valid_agents = ["triage", "format", "questions", "editor"]
        if agent_name not in valid_agents:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid agent_name. Must be one of: {valid_agents}"
            )
        
        # Chat with the specified agent
        result = await unified_agent_system.chat(session_id, request.message, agent_name, user_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in unified chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during agent interaction")


@unified_router.get("/session/{session_id}/status", response_model=Dict[str, Any])
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current session status and progress"""
    try:
        # Get context from the unified system
        context = unified_agent_system._get_or_create_context(session_id, current_user["email"])
        
        return {
            "session_id": session_id,
            "progress": {
                "format_completed": context.format_completed,
                "questions_completed": context.questions_completed,
                "editing_completed": context.editing_completed
            },
            "exam_info": {
                "title": context.exam_title,
                "subject": context.subject,
                "num_questions": context.num_questions,
                "time_limit": context.time_limit,
                "difficulty_level": context.difficulty_level,
                "questions_count": len(context.questions)
            },
            "conversation_count": len(context.conversation_history),
            "last_interaction": context.conversation_history[-1] if context.conversation_history else None
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unified_router.get("/session/{session_id}/context", response_model=Dict[str, Any])
async def get_session_context(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get complete session context and conversation history"""
    try:
        # Get context from the unified system
        context = unified_agent_system._get_or_create_context(session_id, current_user["email"])
        
        return {
            "session_id": session_id,
            "context_data": context.model_dump(),
            "conversation_history": context.conversation_history,
            "progress_summary": {
                "format_completed": context.format_completed,
                "questions_completed": context.questions_completed,
                "editing_completed": context.editing_completed,
                "total_questions": len(context.questions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unified_router.get("/session/{session_id}/export")
async def export_exam(
    session_id: str,
    format: str = Query(default="json", description="Export format: json, markdown"),
    current_user: dict = Depends(get_current_user)
):
    """Export completed exam in specified format"""
    try:
        # Get context from the unified system
        context = unified_agent_system._get_or_create_context(session_id, current_user["email"])
        
        if not context.format_completed:
            raise HTTPException(status_code=400, detail="Exam format not completed")
        
        if not context.questions_completed:
            raise HTTPException(status_code=400, detail="Questions not completed")
        
        exam_data = {
            "exam_info": {
                "title": context.exam_title,
                "subject": context.subject,
                "num_questions": context.num_questions,
                "time_limit": context.time_limit,
                "difficulty_level": context.difficulty_level,
                "question_types": context.question_types
            },
            "format_spec": context.format_spec,
            "questions": context.questions,
            "quality_assessment": context.quality_assessment if context.editing_completed else None,
            "export_timestamp": context.conversation_history[-1]["timestamp"] if context.conversation_history else None
        }
        
        if format == "json":
            return exam_data
        elif format == "markdown":
            # Convert to markdown format
            markdown_content = f"# {context.exam_title}\n\n"
            markdown_content += f"**Subject:** {context.subject}\n"
            markdown_content += f"**Time Limit:** {context.time_limit} minutes\n"
            markdown_content += f"**Difficulty:** {context.difficulty_level}\n\n"
            
            for i, question in enumerate(context.questions, 1):
                markdown_content += f"## Question {i}\n\n"
                markdown_content += f"{question.get('question', '')}\n\n"
                if question.get('options'):
                    for opt_key, opt_value in question['options'].items():
                        markdown_content += f"- {opt_key}: {opt_value}\n"
                markdown_content += f"\n**Answer:** {question.get('answer', '')}\n\n"
            
            return {"content": markdown_content, "filename": f"{context.exam_title.replace(' ', '_')}.md"}
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'markdown'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting exam: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unified_router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete session and all associated data"""
    try:
        success = unified_agent_system.context_manager.cleanup_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found or could not be deleted")
        
        return {"message": "Session deleted successfully", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unified_router.get("/workflow/info")
async def get_workflow_info():
    """Get information about the unified workflow system with OpenAI Agents SDK"""
    return {
        "workflow": {
            "description": "Unified exam creation workflow with OpenAI Agents SDK and intelligent handoffs",
            "sdk": "OpenAI Agents SDK with context management and automatic handoffs",
            "process": [
                "1. Start with triage agent for intelligent routing",
                "2. Triage routes to format agent for exam structure",
                "3. Format agent works iteratively, uses tools to save progress",
                "4. Format agent hands back to triage when complete",
                "5. Triage routes to questions agent for content creation",
                "6. Questions agent generates and refines questions, saves via tools",
                "7. Questions agent hands back to triage when complete",
                "8. Triage routes to editor agent for quality review",
                "9. Editor agent reviews and improves exam quality, saves assessment",
                "10. Process complete when all phases finished"
            ]
        },
        "agents": {
            "triage": {
                "role": "Intelligent router with context awareness",
                "routes_to": ["format", "questions", "editor"],
                "when_to_use": "Start here, or after any agent completes their task",
                "features": ["Dynamic instructions", "Progress tracking", "Smart routing"]
            },
            "format": {
                "role": "Creates exam format and structure",
                "tools": ["save_exam_format", "get_context_summary"],
                "completes_when": "All format specifications gathered and saved",
                "hands_off_to": "triage",
                "features": ["Context-aware instructions", "Tool integration"]
            },
            "questions": {
                "role": "Generates exam questions and answers",
                "tools": ["save_questions", "get_context_summary"],
                "completes_when": "User approves all questions and they're saved",
                "hands_off_to": "triage",
                "features": ["Format-aware generation", "Quality validation", "Iterative refinement"]
            },
            "editor": {
                "role": "Reviews and improves exam quality",
                "tools": ["update_quality_assessment", "get_context_summary"],
                "completes_when": "Exam meets quality standards and assessment saved",
                "hands_off_to": "triage",
                "features": ["Quality analysis", "Improvement suggestions", "Final validation"]
            }
        },
        "features": {
            "context_management": "Persistent context across all agents",
            "handoffs": "Automatic agent-to-agent handoffs",
            "tools": "Function tools for state persistence",
            "dynamic_instructions": "Context-aware agent instructions",
            "progress_tracking": "Real-time progress monitoring"
        },
        "usage": {
            "endpoint": "/exam/chat",
            "parameters": {
                "agent_name": "Which agent to interact with (start with 'triage')",
                "message": "Your message to the agent",
                "session_id": "Optional - for conversation continuity"
            },
            "response": {
                "agent_name": "Which agent handled the request (may differ due to handoffs)",
                "message": "Agent's response",
                "context_data": "Current context state",
                "conversation_history": "Recent conversation"
            }
        }
    }


@unified_router.get("/agents/status")
async def get_agents_status():
    """Get status of all available agents"""
    try:
        agents_info = {}
        for agent_name, agent in unified_agent_system.agents.items():
            agents_info[agent_name] = {
                "name": agent.name,
                "model": agent.model,
                "handoff_description": agent.handoff_description,
                "has_tools": len(agent.tools) > 0,
                "tool_count": len(agent.tools),
                "tool_names": [tool.name for tool in agent.tools],
                "has_handoffs": len(agent.handoffs) > 0,
                "handoff_count": len(agent.handoffs)
            }
        
        return {
            "total_agents": len(unified_agent_system.agents),
            "agents": agents_info,
            "sdk_version": "OpenAI Agents SDK",
            "features": {
                "context_management": True,
                "automatic_handoffs": True,
                "function_tools": True,
                "dynamic_instructions": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@unified_router.get("/health")
async def health_check():
    """Health check for unified exam system"""
    try:
        redis_connected = unified_agent_system.context_manager.redis_client is not None
        agent_count = len(unified_agent_system.agents)
        
        # Test context creation
        test_context = unified_agent_system._get_or_create_context("health_check", "test_user")
        context_working = test_context is not None
        
        return {
            "status": "healthy",
            "agents_available": agent_count,
            "agent_names": list(unified_agent_system.agents.keys()),
            "redis_connected": redis_connected,
            "context_system": "working" if context_working else "error",
            "workflow_type": "openai_agents_sdk",
            "features": {
                "handoffs": True,
                "tools": True,
                "context_persistence": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e)
        }