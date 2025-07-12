from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, ValidationError
from typing import Optional, List, Dict, Any
import logging

from my_agents.models.quiz_models import (
    CreateQuizRequest, QuizSummary, QuizForTaking, SubmitQuizRequest, 
    QuizAttempt, ValidateAnswerRequest, ValidateAnswerResponse,
    QuizListResponse, QuizResponse, UserQuizStats, GenerateQuizRequest,
    GenerateQuizResponse
)
from services.quiz_service import QuizService
from my_agents.quiz_generation_agent import QuizGenerationAgent

router = APIRouter(prefix="/api/v1/quiz", tags=["quiz"])
logger = logging.getLogger(__name__)

# Initialize services
try:
    quiz_service = QuizService()
    quiz_generation_agent = QuizGenerationAgent()
except Exception as e:
    logger.warning(f"Failed to initialize quiz services: {e}")
    quiz_service = None
    quiz_generation_agent = None


@router.post("/quiz/create", response_model=QuizResponse)
async def create_quiz(request: CreateQuizRequest):
    """Create a new quiz manually"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        # Convert Pydantic model to dict
        quiz_data = request.model_dump()
        
        # Create quiz
        quiz_id = quiz_service.create_quiz(quiz_data)
        
        if not quiz_id:
            raise HTTPException(status_code=500, detail="Failed to create quiz")
        
        # Get created quiz summary
        quiz = quiz_service.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=500, detail="Failed to retrieve created quiz")
        
        quiz_summary = QuizSummary(
            quiz_id=quiz["quiz_id"],
            title=quiz["title"],
            description=quiz.get("description"),
            created_at=quiz["created_at"],
            created_by=quiz["created_by"],
            question_count=len(quiz["questions"]),
            total_points=sum(q.get("points", 1) for q in quiz["questions"]),
            time_limit=quiz.get("time_limit"),
            allow_multiple_attempts=quiz.get("allow_multiple_attempts", True),
            shuffle_questions=quiz.get("shuffle_questions", False)
        )
        
        return QuizResponse(
            success=True,
            message="Quiz created successfully",
            data={"quiz_id": quiz_id, "quiz_summary": quiz_summary.model_dump()}
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quiz/health", response_model=QuizResponse)
async def health_check():
    """Health check endpoint for quiz service"""
    try:
        # Test Redis connection
        if not quiz_service or not quiz_service.client:
            raise HTTPException(status_code=503, detail="Quiz service unavailable - Redis not connected")
        
        # Try to ping Redis
        quiz_service.client.ping()
        
        # Check Redis data
        quiz_keys = quiz_service.client.keys('quiz:*')
        quiz_ids = quiz_service.client.smembers('quiz_index')
        
        return QuizResponse(
            success=True,
            message=f"Quiz service is healthy. Found {len(quiz_keys)} quiz keys and {len(quiz_ids)} quiz IDs in index",
            data={
                "quiz_keys_count": len(quiz_keys),
                "quiz_index_count": len(quiz_ids),
                "redis_connected": True
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")



@router.get("/quiz/list", response_model=QuizListResponse)
async def list_quizzes(limit: int = Query(default=50, ge=1, le=100)):
    """List all available quizzes"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        quizzes = quiz_service.list_quizzes(limit)
        quiz_summaries = [QuizSummary(**quiz) for quiz in quizzes]
        
        return QuizListResponse(
            quizzes=quiz_summaries,
            total_count=len(quiz_summaries)
        )
        
    except Exception as e:
        logger.error(f"Error listing quizzes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str):
    """Get quiz details for taking (questions without answers)"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        quiz = quiz_service.get_quiz(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Get questions without correct answers
        questions = quiz_service.get_quiz_questions(quiz_id)
        if questions is None:
            raise HTTPException(status_code=404, detail="Quiz questions not found")
        
        quiz_for_taking = QuizForTaking(
            quiz_id=quiz["quiz_id"],
            title=quiz["title"],
            description=quiz.get("description"),
            questions=questions,
            total_points=sum(q.get("points", 1) for q in quiz["questions"]),
            time_limit=quiz.get("time_limit"),
            allow_multiple_attempts=quiz.get("allow_multiple_attempts", True),
            shuffle_questions=quiz.get("shuffle_questions", False)
        )
        
        return QuizResponse(
            success=True,
            message="Quiz retrieved successfully",
            data=quiz_for_taking.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/quiz/submit", response_model=QuizResponse)
async def submit_quiz(request: SubmitQuizRequest):
    """Submit quiz answers and get results"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        # Convert answers to dict format
        answers = [answer.model_dump() for answer in request.answers]
        
        # Submit quiz attempt
        attempt = quiz_service.submit_quiz_attempt(
            request.quiz_id, 
            request.user_id, 
            answers
        )
        
        if not attempt:
            raise HTTPException(status_code=500, detail="Failed to submit quiz")
        
        # Convert to Pydantic model
        quiz_attempt = QuizAttempt(**attempt)
        
        return QuizResponse(
            success=True,
            message="Quiz submitted successfully",
            data=quiz_attempt.model_dump()
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quiz/attempt/{attempt_id}", response_model=QuizResponse)
async def get_quiz_attempt(attempt_id: str):
    """Get quiz attempt results"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        attempt = quiz_service.get_quiz_attempt(attempt_id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Quiz attempt not found")
        
        quiz_attempt = QuizAttempt(**attempt)
        
        return QuizResponse(
            success=True,
            message="Quiz attempt retrieved successfully",
            data=quiz_attempt.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quiz attempt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quiz/user/{user_id}/attempts", response_model=QuizResponse)
async def get_user_attempts(user_id: str, limit: int = Query(default=10, ge=1, le=50)):
    """Get all quiz attempts for a user"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        attempts = quiz_service.get_user_attempts(user_id)
        
        # Limit results
        limited_attempts = attempts[:limit]
        
        # Calculate user stats
        if attempts:
            total_attempts = len(attempts)
            scores = [attempt.get("score_percentage", 0) for attempt in attempts]
            average_score = sum(scores) / len(scores)
            best_score = max(scores)
            
            # Count unique quizzes taken
            unique_quizzes = set(attempt.get("quiz_id") for attempt in attempts)
            quizzes_taken = len(unique_quizzes)
            
            user_stats = UserQuizStats(
                user_id=user_id,
                total_attempts=total_attempts,
                average_score=average_score,
                best_score=best_score,
                quizzes_taken=quizzes_taken,
                recent_attempts=[QuizAttempt(**attempt) for attempt in limited_attempts]
            )
        else:
            user_stats = UserQuizStats(
                user_id=user_id,
                total_attempts=0,
                average_score=0.0,
                best_score=0.0,
                quizzes_taken=0,
                recent_attempts=[]
            )
        
        return QuizResponse(
            success=True,
            message="User attempts retrieved successfully",
            data=user_stats.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user attempts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/quiz/validate-answer", response_model=ValidateAnswerResponse)
async def validate_answer(request: ValidateAnswerRequest):
    """Validate a single answer"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        result = quiz_service.validate_answer(
            request.quiz_id,
            request.question_id,
            request.user_answer
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return ValidateAnswerResponse(**result)
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating answer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/quiz/{quiz_id}", response_model=QuizResponse)
async def delete_quiz(quiz_id: str):
    """Delete a quiz"""
    if not quiz_service:
        raise HTTPException(status_code=503, detail="Quiz service unavailable")
    
    try:
        success = quiz_service.delete_quiz(quiz_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Quiz not found or could not be deleted")
        
        return QuizResponse(
            success=True,
            message="Quiz deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/quiz/generate", response_model=GenerateQuizResponse)
async def generate_quiz_from_document(request: GenerateQuizRequest):
    """Generate a quiz from document text using AI"""
    if not quiz_service or not quiz_generation_agent:
        raise HTTPException(status_code=503, detail="Quiz service or AI agent unavailable")
    
    try:
        # Process the request using the quiz generation agent
        result = await quiz_generation_agent.process(request.model_dump(), {})
        
        if not result or "quiz_id" not in result:
            raise HTTPException(status_code=500, detail="Failed to generate quiz")
        
        # Get the created quiz for summary
        quiz = quiz_service.get_quiz(result["quiz_id"])
        if not quiz:
            raise HTTPException(status_code=500, detail="Failed to retrieve generated quiz")
        
        quiz_summary = QuizSummary(
            quiz_id=quiz["quiz_id"],
            title=quiz["title"],
            description=quiz.get("description"),
            created_at=quiz["created_at"],
            created_by=quiz["created_by"],
            question_count=len(quiz["questions"]),
            total_points=sum(q.get("points", 1) for q in quiz["questions"]),
            time_limit=quiz.get("time_limit"),
            allow_multiple_attempts=quiz.get("allow_multiple_attempts", True),
            shuffle_questions=quiz.get("shuffle_questions", False)
        )
        
        return GenerateQuizResponse(
            quiz_id=result["quiz_id"],
            message="Quiz generated successfully from document",
            quiz_summary=quiz_summary
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


