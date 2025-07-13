"""
Exam Agents Module

Multi-agent examination generation system with two interaction models:
1. Standalone agents for direct client interaction (conversational)
2. Workflow agents for automated handoff coordination

Provides comprehensive exam creation with specialized agents for format, questions, and editing.
"""

# Workflow-based agents (automated handoff)
from .schemas import ExaminationRequest, ExamGenerationResult
from .context import ExamContextManager

# Standalone agents (direct interaction)

# API routes

__all__ = [
    # Workflow system
    'exam_workflow',
    'ExaminationRequest', 
    'ExamGenerationResult',
    'ExamContextManager',
    
    # Standalone system
    'EXAM_AGENTS',
    'AgentInteractionResult',
    'ExamFormatAgent',
    'QuestionGeneratorAgent',
    'ExamEditorAgent', 
    'ExamManagerAgent',
    
    # API
    'exam_agents_router'
]