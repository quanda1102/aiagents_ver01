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
    grading_criteria: str,
    learning_objectives: str
) -> str:
    """Save exam format specification to context."""
    context.context.exam_title = title
    context.context.subject = subject
    context.context.num_questions = num_questions
    context.context.time_limit = time_limit
    context.context.difficulty_level = difficulty_level
    context.context.question_types = question_types.split(',')
    
    context.context.format_spec = {
        "title": title,
        "subject": subject,
        "num_questions": num_questions,
        "time_limit": time_limit,
        "difficulty_level": difficulty_level,
        "question_types": question_types.split(','),
        "grading_criteria": grading_criteria,
        "learning_objectives": learning_objectives
    }
    context.context.format_completed = True
    
    return f"Exam format saved: {title} - {subject} with {num_questions} questions"

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
        "YOUR ROLE:\n"
        "1. Work iteratively with the user to create a complete exam format\n"
        "2. Ask focused questions to gather all required format information\n"
        "3. Use save_exam_format tool when you have collected ALL necessary information\n"
        "4. After saving, transfer back to triage agent\n\n"
        "REQUIRED INFORMATION:\n"
        "- Exam title and subject\n"
        "- Number of questions and time limit\n"
        "- Question type distribution (multiple choice, essay, etc.)\n"
        "- Difficulty levels\n"
        "- Grading criteria\n"
        "- Learning objectives\n"
        "- Special instructions\n\n"
        "Work iteratively until you have everything needed for a complete exam format."
    )

format_agent = Agent[ExamAgentContext](
    name="Format Agent",
    model="gpt-4o",
    handoff_description="Specialist agent for creating exam formats and structures",
    instructions=format_agent_instructions,
    tools=[save_exam_format, get_context_summary],
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
        "CRITICAL BEHAVIOR:\n"
        "- You NEVER create exams yourself\n"
        "- You NEVER provide exam content directly\n"
        "- You ONLY analyze requests and hand off to specialists\n"
        "- You ALWAYS use handoffs to delegate work\n\n"
        "HANDOFF LOGIC:\n"
        "- Format not complete OR user mentions 'format/structure' → Hand off to format agent\n"
        "- Format complete but questions not complete OR user mentions 'questions/generate' → Hand off to questions agent\n"
        "- Questions complete but editing not complete OR user mentions 'review/edit/improve' → Hand off to editor agent\n"
        "- All complete → Congratulate user and offer to start new exam\n\n"
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
            
            # Determine which agent handled the final response
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
            
            return UnifiedAgentResponse(
                success=True,
                session_id=session_id,
                agent_name=final_agent_name,
                message=message,
                context_data=context.model_dump(),
                conversation_history=context.conversation_history[-5:]  # Last 5 exchanges
            )
            
        except Exception as e:
            logger.error(f"Error in unified agent chat: {e}")
            return UnifiedAgentResponse(
                success=False,
                session_id=session_id,
                agent_name=agent_name,
                message=f"Error occurred: {str(e)}",
                context_data={},
                conversation_history=[]
            )
    
    def _get_or_create_context(self, session_id: str, user_id: str) -> ExamAgentContext:
        """Get existing context or create new one"""
        session_data = self.context_manager.get_session_data(session_id)
        if session_data:
            # Convert stored data back to context
            return ExamAgentContext(**session_data)
        else:
            # Create new context
            return create_initial_context(session_id, user_id)
    
    def _store_context(self, session_id: str, context: ExamAgentContext) -> None:
        """Store context data"""
        self.context_manager._store_session_data(session_id, context.model_dump())


# Create global instance
unified_agent_system = UnifiedExamAgentSystem()