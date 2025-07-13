"""
Unified Exam Agent System
Single endpoint where agent_name parameter determines which agent to call.
Agents decide when they're finished and hand off to manager for routing.
"""
from __future__ import annotations

import asyncio
import json
import random
import string
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    function_tool,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from .context import ExamContextManager
from .schemas import ExaminationRequest
import logging

logger = logging.getLogger(__name__)

# =========================
# CONTEXT
# =========================

class ExamAgentContext(BaseModel):
    """Context for exam creation agents."""
    session_id: str | None = None
    user_id: str | None = None
    exam_title: str | None = None
    subject: str | None = None
    num_questions: int | None = None
    time_limit: int | None = None
    difficulty_level: str | None = None
    question_types: List[str] = Field(default_factory=list)
    format_completed: bool = False
    questions_completed: bool = False
    editing_completed: bool = False
    format_spec: Dict[str, Any] = Field(default_factory=dict)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    quality_assessment: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

def create_initial_context(session_id: str, user_id: str) -> ExamAgentContext:
    """Factory for a new ExamAgentContext."""
    return ExamAgentContext(
        session_id=session_id,
        user_id=user_id
    )

# =========================
# TOOLS
# =========================

@function_tool(
    name_override="save_exam_format",
    description_override="Save the exam format specification to context."
)
async def save_exam_format(
    context: RunContextWrapper[ExamAgentContext],
    title: str,
    subject: str,
    num_questions: int,
    time_limit: int,
    difficulty_level: str,
    question_types: str,
    grading_criteria: str = "Standard academic grading: 90-100% A, 80-89% B, 70-79% C, 60-69% D, below 60% F",
    learning_objectives: str = "To be determined based on subject and requirements"
) -> str:
    """Save exam format specification to context."""
    try:
        # Parse question types
        parsed_question_types = [qt.strip() for qt in question_types.split(',')]
        
        # Update context
        context.context.exam_title = title
        context.context.subject = subject
        context.context.num_questions = num_questions
        context.context.time_limit = time_limit
        context.context.difficulty_level = difficulty_level
        context.context.question_types = parsed_question_types
        
        context.context.format_spec = {
            "title": title,
            "subject": subject,
            "num_questions": num_questions,
            "time_limit": time_limit,
            "difficulty_level": difficulty_level,
            "question_types": parsed_question_types,
            "grading_criteria": grading_criteria,
            "learning_objectives": learning_objectives
        }
        context.context.format_completed = True
        
        return f"Exam format saved successfully: '{title}' in {subject} with {num_questions} questions, {time_limit} minutes, {difficulty_level} difficulty, question types: {', '.join(parsed_question_types)}"
        
    except Exception as e:
        return f"Error saving exam format: {str(e)}"

@function_tool(
    name_override="save_questions",
    description_override="Save generated questions to context."
)
async def save_questions(
    context: RunContextWrapper[ExamAgentContext],
    questions_json: str
) -> str:
    """Save generated questions to context."""
    try:
        questions = json.loads(questions_json)
        context.context.questions = questions
        context.context.questions_completed = True
        return f"Saved {len(questions)} questions to exam"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for questions"

@function_tool(
    name_override="update_quality_assessment",
    description_override="Update quality assessment results."
)
async def update_quality_assessment(
    context: RunContextWrapper[ExamAgentContext],
    assessment_json: str
) -> str:
    """Update quality assessment results."""
    try:
        assessment = json.loads(assessment_json)
        context.context.quality_assessment = assessment
        context.context.editing_completed = True
        return "Quality assessment completed and saved"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for assessment"

@function_tool(
    name_override="get_context_summary",
    description_override="Get a summary of current exam creation progress."
)
async def get_context_summary(
    context: RunContextWrapper[ExamAgentContext]
) -> str:
    """Get a summary of current exam creation progress."""
    ctx = context.context
    summary = {
        "session_id": ctx.session_id,
        "format_completed": ctx.format_completed,
        "questions_completed": ctx.questions_completed,
        "editing_completed": ctx.editing_completed,
        "exam_title": ctx.exam_title,
        "subject": ctx.subject,
        "num_questions": ctx.num_questions,
        "questions_count": len(ctx.questions)
    }
    return json.dumps(summary, indent=2)

@function_tool(
    name_override="extract_exam_requirements",
    description_override="Extract exam requirements from user message and update context."
)
async def extract_exam_requirements(
    context: RunContextWrapper[ExamAgentContext],
    user_message: str
) -> str:
    """Extract exam requirements from user message and update context."""
    try:
        message_lower = user_message.lower()
        extracted_info = []
        
        # Extract number of questions (English and Vietnamese)
        import re
        num_questions_match = re.search(r'(\d+)\s*(?:questions?|câu hỏi|câu)', message_lower)
        if num_questions_match:
            context.context.num_questions = int(num_questions_match.group(1))
            extracted_info.append(f"Number of questions: {context.context.num_questions}")
        
        # Extract time limit (English and Vietnamese)
        time_match = re.search(r'(\d+)\s*(?:minutes?|phút|phút)', message_lower)
        if time_match:
            context.context.time_limit = int(time_match.group(1))
            extracted_info.append(f"Time limit: {context.context.time_limit} minutes")
        
        # Extract difficulty level (English and Vietnamese)
        if any(word in message_lower for word in ['mixed', 'hỗn hợp', 'trộn lẫn']) or \
           (any(word in message_lower for word in ['easy', 'dễ']) and 
            any(word in message_lower for word in ['medium', 'trung bình', 'vừa']) and 
            any(word in message_lower for word in ['hard', 'khó', 'difficult'])):
            context.context.difficulty_level = "mixed"
            extracted_info.append("Difficulty level: mixed")
        elif any(word in message_lower for word in ['easy', 'dễ']):
            context.context.difficulty_level = "easy"
            extracted_info.append("Difficulty level: easy")
        elif any(word in message_lower for word in ['medium', 'trung bình', 'vừa']):
            context.context.difficulty_level = "medium"
            extracted_info.append("Difficulty level: medium")
        elif any(word in message_lower for word in ['hard', 'khó', 'difficult']):
            context.context.difficulty_level = "hard"
            extracted_info.append("Difficulty level: hard")
        
        # Extract question types (English and Vietnamese)
        question_types = []
        if any(phrase in message_lower for phrase in ['multiple choice', 'trắc nghiệm', 'nhiều lựa chọn']):
            question_types.append("multiple choice")
        if any(phrase in message_lower for phrase in ['true/false', 'true false', 'đúng/sai', 'đúng sai']):
            question_types.append("true/false")
        if any(phrase in message_lower for phrase in ['short answer', 'câu trả lời ngắn', 'trả lời ngắn']):
            question_types.append("short answer")
        if any(phrase in message_lower for phrase in ['essay', 'tự luận', 'viết luận']):
            question_types.append("essay")
        if any(phrase in message_lower for phrase in ['fill in the blank', 'fill-in-the-blank', 'điền vào chỗ trống', 'điền khuyết']):
            question_types.append("fill in the blank")
        
        if question_types:
            context.context.question_types = question_types
            extracted_info.append(f"Question types: {', '.join(question_types)}")
        
        # Extract grading criteria (English and Vietnamese)
        grading_match = re.search(r'(\d+)%.*(?:pass|passing|qua|đậu|điểm qua)', message_lower)
        if grading_match:
            passing_grade = grading_match.group(1)
            grading_criteria = f"Passing grade: {passing_grade}%"
            if not context.context.format_spec.get('grading_criteria'):
                context.context.format_spec['grading_criteria'] = grading_criteria
            extracted_info.append(f"Grading criteria: {grading_criteria}")
        
        if extracted_info:
            return f"Extracted information: {'; '.join(extracted_info)}"
        else:
            return "No specific exam requirements found in the message."
            
    except Exception as e:
        return f"Error extracting requirements: {str(e)}"

# =========================
# HANDOFF HOOKS
# =========================

async def on_format_handoff(context: RunContextWrapper[ExamAgentContext]) -> None:
    """Initialize format creation process."""
    logger.info(f"Handoff to format agent for session {context.context.session_id}")

async def on_questions_handoff(context: RunContextWrapper[ExamAgentContext]) -> None:
    """Initialize question generation process."""
    logger.info(f"Handoff to questions agent for session {context.context.session_id}")

async def on_editor_handoff(context: RunContextWrapper[ExamAgentContext]) -> None:
    """Initialize editing process."""
    logger.info(f"Handoff to editor agent for session {context.context.session_id}")

# =========================
# AGENTS
# =========================

def format_agent_instructions(
    run_context: RunContextWrapper[ExamAgentContext], agent: Agent[ExamAgentContext]
) -> str:
    """Dynamic instructions for format agent based on context."""
    ctx = run_context.context
    progress = "Starting fresh" if not ctx.format_completed else "Format already completed"
    
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        f"You are the Format Agent, specialist in creating exam formats and structures.\n"
        f"Current status: {progress}\n\n"
        "LANGUAGE SUPPORT:\n"
        "- Always respond in the same language as the user (Vietnamese or English)\n"
        "- Support both Vietnamese and English exam creation\n\n"
        "YOUR ROLE:\n"
        "1. Use extract_exam_requirements tool to extract information from user messages\n"
        "2. Use save_exam_format tool when you have sufficient information\n"
        "3. Only ask for missing ESSENTIAL information (title, subject, learning objectives)\n"
        "4. After saving, transfer back to triage agent\n\n"
        "WORKFLOW:\n"
        "1. Always start by using extract_exam_requirements tool on user messages\n"
        "2. Check what information is still missing after extraction\n"
        "3. Ask only for missing essential information\n"
        "4. Use save_exam_format when you have enough information\n\n"
        "REQUIRED INFORMATION FOR SAVE_EXAM_FORMAT:\n"
        "- title: Ask user for exam title if not provided\n"
        "- subject: Ask user for subject if not provided\n"
        "- num_questions: Extract from user message or ask\n"
        "- time_limit: Extract from user message or ask\n"
        "- difficulty_level: Extract from user message or ask\n"
        "- question_types: Extract from user message or ask\n"
        "- grading_criteria: Extract from user message or use default\n"
        "- learning_objectives: Ask user for learning objectives if not provided\n\n"
        "EFFICIENCY: Use extract_exam_requirements first, then ask only for missing essentials."
    )

format_agent = Agent[ExamAgentContext](
    name="Format Agent",
    model="gpt-4o",
    handoff_description="Specialist agent for creating exam formats and structures",
    instructions=format_agent_instructions,
    tools=[save_exam_format, extract_exam_requirements, get_context_summary],
)

def questions_agent_instructions(
    run_context: RunContextWrapper[ExamAgentContext], agent: Agent[ExamAgentContext]
) -> str:
    """Dynamic instructions for questions agent based on context."""
    ctx = run_context.context
    format_info = f"Format: {ctx.exam_title} - {ctx.subject}" if ctx.format_completed else "No format available"
    
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        f"You are the Question Generator Agent, specialist in creating high-quality exam questions.\n"
        f"Current context: {format_info}\n\n"
        "LANGUAGE SUPPORT:\n"
        "- Always respond in the same language as the user (Vietnamese or English)\n"
        "- Generate questions in the same language as the user\n\n"
        "YOUR ROLE:\n"
        "1. Generate questions based on format specifications\n"
        "2. Work iteratively with user to refine questions\n"
        "3. Use save_questions tool when user approves all questions\n"
        "4. After saving, transfer back to triage agent\n\n"
        "YOUR WORK:\n"
        "- Generate questions according to format specifications\n"
        "- Provide proper answers and explanations\n"
        "- Allow user feedback and revisions\n"
        "- Ensure questions meet quality standards\n\n"
        "Work iteratively until you have a complete set of approved questions."
    )

questions_agent = Agent[ExamAgentContext](
    name="Questions Agent",
    model="gpt-4o",
    handoff_description="Specialist agent for creating high-quality exam questions",
    instructions=questions_agent_instructions,
    tools=[save_questions, get_context_summary],
)

def editor_agent_instructions(
    run_context: RunContextWrapper[ExamAgentContext], agent: Agent[ExamAgentContext]
) -> str:
    """Dynamic instructions for editor agent based on context."""
    ctx = run_context.context
    progress = f"Questions: {len(ctx.questions)} available" if ctx.questions_completed else "No questions available"
    
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        f"You are the Editor Agent, specialist in quality review and exam improvement.\n"
        f"Current context: {progress}\n\n"
        "LANGUAGE SUPPORT:\n"
        "- Always respond in the same language as the user (Vietnamese or English)\n"
        "- Review and improve exams in the same language as the user\n\n"
        "YOUR ROLE:\n"
        "1. Review completed exam (format + questions) for quality\n"
        "2. Suggest improvements and work with user to implement them\n"
        "3. Use update_quality_assessment tool when review is complete\n"
        "4. After assessment, transfer back to triage agent\n\n"
        "YOUR WORK:\n"
        "- Review exam structure and questions for quality\n"
        "- Check for errors, bias, clarity issues\n"
        "- Suggest specific improvements\n"
        "- Validate final exam quality\n\n"
        "Work iteratively until the exam meets high quality standards."
    )

editor_agent = Agent[ExamAgentContext](
    name="Editor Agent",
    model="gpt-4o",
    handoff_description="Specialist agent for quality review and exam improvement",
    instructions=editor_agent_instructions,
    tools=[update_quality_assessment, get_context_summary],
)

def triage_agent_instructions(
    run_context: RunContextWrapper[ExamAgentContext], agent: Agent[ExamAgentContext]
) -> str:
    """Dynamic instructions for triage agent based on context."""
    ctx = run_context.context
    status = {
        "format": "✓" if ctx.format_completed else "○",
        "questions": "✓" if ctx.questions_completed else "○",
        "editing": "✓" if ctx.editing_completed else "○"
    }
    
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        f"You are the Triage Agent. You are a ROUTER that delegates to appropriate specialists.\n"
        f"Current progress: Format {status['format']} | Questions {status['questions']} | Editing {status['editing']}\n\n"
        "LANGUAGE SUPPORT:\n"
        "- Always respond in the same language as the user (Vietnamese or English)\n"
        "- Support both Vietnamese and English exam creation\n\n"
        "CRITICAL BEHAVIOR:\n"
        "- You NEVER create exams yourself\n"
        "- You NEVER provide exam content directly\n"
        "- You ONLY analyze requests and hand off to specialists\n"
        "- You ALWAYS use handoffs to delegate work\n"
        "- When users provide detailed requirements, immediately hand off to format agent\n\n"
        "HANDOFF LOGIC:\n"
        "- Format not complete AND user provides exam requirements (questions, time, difficulty, etc.) → Hand off to format agent immediately\n"
        "- Format not complete AND user only gives basic info → Hand off to format agent\n"
        "- Format complete but questions not complete → Hand off to questions agent\n"
        "- Questions complete but editing not complete → Hand off to editor agent\n"
        "- All complete → Congratulate user and offer to start new exam\n\n"
        "IMPORTANT: If user mentions specific exam requirements (number of questions, time limit, difficulty, question types, grading criteria), "
        "don't ask for more details - immediately hand off to format agent who will gather any missing information.\n\n"
        "You are a pure router. Immediately hand off to the right specialist."
    )

triage_agent = Agent[ExamAgentContext](
    name="Triage Agent",
    model="gpt-4o",
    handoff_description="Router agent that delegates to appropriate specialists",
    instructions=triage_agent_instructions,
    tools=[get_context_summary],
    handoffs=[
        handoff(agent=format_agent, on_handoff=on_format_handoff),
        handoff(agent=questions_agent, on_handoff=on_questions_handoff),
        handoff(agent=editor_agent, on_handoff=on_editor_handoff),
    ],
)

# Set up handoff relationships - specialist agents can hand back to triage
format_agent.handoffs = [triage_agent]
questions_agent.handoffs = [triage_agent]
editor_agent.handoffs = [triage_agent]

# =========================
# UNIFIED RESPONSE MODEL
# =========================

class UnifiedAgentResponse(BaseModel):
    """Response from unified agent interaction"""
    success: bool = Field(description="Whether the interaction was successful")
    session_id: str = Field(description="Session identifier")
    agent_name: str = Field(description="Name of the agent that handled the request")
    message: str = Field(description="Agent's response message")
    context_data: Dict[str, Any] = Field(default={}, description="Updated context data")
    conversation_history: List[Dict[str, Any]] = Field(default=[], description="Recent conversation")

# =========================
# UNIFIED SYSTEM
# =========================

class UnifiedExamAgentSystem:
    """Unified system where all agents share the same endpoint"""
    
    def __init__(self):
        self.context_manager = ExamContextManager()
        
        # Agent registry
        self.agents = {
            "triage": triage_agent,
            "format": format_agent,
            "questions": questions_agent,
            "editor": editor_agent
        }
    
    def _determine_next_agent(self, context: ExamAgentContext) -> str:
        """Determine which agent should handle the next user message based on context state"""
        # If nothing is complete, start with triage for routing
        if not context.format_completed and not context.questions_completed and not context.editing_completed:
            return "triage"
        
        # If format not complete, should continue with format agent
        if not context.format_completed:
            return "format"
        
        # If format complete but questions not complete, should go to questions agent
        if context.format_completed and not context.questions_completed:
            return "questions"
        
        # If format and questions complete but editing not complete, should go to editor agent
        if context.format_completed and context.questions_completed and not context.editing_completed:
            return "editor"
        
        # If everything is complete, back to triage for next steps or completion
        return "triage"
    
    async def chat(self, session_id: str, user_message: str, agent_name: str, user_id: str) -> UnifiedAgentResponse:
        """Handle chat with any agent through unified interface"""
        try:
            # Get or create context
            context = self._get_or_create_context(session_id, user_id)
            
            # Get the specified agent
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            agent = self.agents[agent_name]
            
            # Add user message to conversation history
            context.conversation_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "role": "user",
                "message": user_message,
                "agent": agent_name
            })
            
            # Run the agent with context - handoffs handled automatically by SDK
            result = await Runner.run(agent, user_message, context=context)
            
            # Extract response
            if hasattr(result, 'final_output'):
                message = str(result.final_output)
            else:
                message = str(result)
            
            # Determine which agent handled the final response (for conversation history)
            final_agent_name = agent_name
            if hasattr(result, 'agent') and hasattr(result.agent, 'name'):
                final_agent_name = result.agent.name
            
            # Add agent response to conversation
            context.conversation_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "role": "agent",
                "message": message,
                "agent": final_agent_name
            })
            
            # Keep only last 10 conversation entries
            if len(context.conversation_history) > 10:
                context.conversation_history = context.conversation_history[-10:]
            
            # Store updated context
            self._store_context(session_id, context)
            
            # Determine which agent should handle the NEXT user message
            next_agent_name = self._determine_next_agent(context)
            
            # Prepare context data without conversation history
            context_data = context.model_dump()
            context_data.pop('conversation_history', None)  # Remove conversation history from response
            
            return UnifiedAgentResponse(
                success=True,
                session_id=session_id,
                agent_name=next_agent_name,  # Changed to next agent instead of current agent
                message=message,
                context_data=context_data,
                conversation_history=[]  # Cleared conversation history as requested
            )
            
        except Exception as e:
            logger.error(f"Error in unified agent chat: {e}")
            return UnifiedAgentResponse(
                success=False,
                session_id=session_id,
                agent_name=agent_name,
                message=f"Error occurred: {str(e)}",
                context_data={},
                conversation_history=[]  # Also cleared for error response
            )
    
    def _get_or_create_context(self, session_id: str, user_id: str) -> ExamAgentContext:
        """Get existing context or create new one"""
        try:
            # Try to get existing context from Redis
            redis_key = f"exam_context:{session_id}"
            redis_client = self.context_manager.redis_client
            
            if redis_client:
                stored_data = redis_client.get(redis_key)
                if stored_data:
                    context_dict = json.loads(stored_data)
                    # Ensure all required fields are present
                    context_dict.setdefault('session_id', session_id)
                    context_dict.setdefault('user_id', user_id)
                    context_dict.setdefault('question_types', [])
                    context_dict.setdefault('format_spec', {})
                    context_dict.setdefault('questions', [])
                    context_dict.setdefault('quality_assessment', {})
                    context_dict.setdefault('conversation_history', [])
                    
                    return ExamAgentContext(**context_dict)
            
            # Create new context if none exists
            return create_initial_context(session_id, user_id)
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            # Return fresh context on error
            return create_initial_context(session_id, user_id)
    
    def _store_context(self, session_id: str, context: ExamAgentContext) -> None:
        """Store context data in Redis"""
        try:
            redis_key = f"exam_context:{session_id}"
            redis_client = self.context_manager.redis_client
            
            if redis_client:
                # Convert context to dict and store
                context_dict = context.model_dump()
                redis_client.setex(redis_key, 3600, json.dumps(context_dict, default=str))
                logger.info(f"Context stored for session {session_id}")
            else:
                logger.warning("Redis client not available, context not persisted")
                
        except Exception as e:
            logger.error(f"Error storing context: {e}")


# Create global instance
unified_agent_system = UnifiedExamAgentSystem()