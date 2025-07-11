from dotenv import load_dotenv
load_dotenv(override=True)
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from services.redis_manager import get_redis_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuizService:
    def __init__(self):
        """Initialize the Quiz Service with shared Redis connection"""
        self.client = get_redis_client()
        if self.client:
            logger.info("QuizService initialized with shared Redis connection")
        else:
            logger.error("QuizService failed to get Redis connection")

    def create_quiz(self, quiz_data: Dict[str, Any]) -> Optional[str]:
        """Create a new quiz and return quiz_id"""
        if not self.client:
            logger.error("Redis client not available")
            return None
            
        try:
            quiz_id = str(uuid.uuid4())
            quiz_key = f"quiz:{quiz_id}"
            
            # Add metadata to quiz
            quiz_data.update({
                "quiz_id": quiz_id,
                "created_at": datetime.now().isoformat(),
                "created_by": quiz_data.get("created_by", "anonymous")
            })
            
            # Store quiz data
            self.client.set(quiz_key, json.dumps(quiz_data))
            
            # Add to quiz index for listing
            self.client.sadd("quiz_index", quiz_id)
            
            logger.info(f"Created quiz with ID: {quiz_id}")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
            return None

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz by ID"""
        if not self.client:
            logger.error("Redis client not available")
            return None
            
        try:
            quiz_key = f"quiz:{quiz_id}"
            quiz_data = self.client.get(quiz_key)
            
            if quiz_data:
                return json.loads(quiz_data)
            else:
                logger.info(f"Quiz not found: {quiz_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving quiz: {e}")
            return None

    def get_quiz_questions(self, quiz_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get quiz questions without answers (for taking quiz)"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return None
            
        # Remove correct answers from questions
        questions = []
        for q in quiz.get("questions", []):
            question_data = {
                "question_id": q.get("question_id"),
                "question_text": q.get("question_text"),
                "question_type": q.get("question_type"),
                "options": q.get("options", []),
                "points": q.get("points", 1)
            }
            questions.append(question_data)
            
        return questions

    def submit_quiz_attempt(self, quiz_id: str, user_id: str, answers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Submit quiz answers and calculate score"""
        if not self.client:
            logger.error("Redis client not available")
            return None
            
        try:
            quiz = self.get_quiz(quiz_id)
            if not quiz:
                return None
                
            # Calculate score
            total_points = 0
            earned_points = 0
            results = []
            
            for question in quiz.get("questions", []):
                q_id = question.get("question_id")
                correct_answer = question.get("correct_answer")
                points = question.get("points", 1)
                total_points += points
                
                # Find user's answer
                user_answer = None
                for answer in answers:
                    if answer.get("question_id") == q_id:
                        user_answer = answer.get("answer")
                        break
                
                # Check if correct
                is_correct = False
                if question.get("question_type") == "multiple_choice":
                    is_correct = user_answer == correct_answer
                elif question.get("question_type") == "true_false":
                    is_correct = user_answer == correct_answer
                elif question.get("question_type") == "text":
                    # For text questions, do basic string comparison (case-insensitive)
                    is_correct = str(user_answer).lower().strip() == str(correct_answer).lower().strip()
                
                if is_correct:
                    earned_points += points
                    
                results.append({
                    "question_id": q_id,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "points": points if is_correct else 0
                })
            
            # Store attempt
            attempt_id = str(uuid.uuid4())
            attempt_data = {
                "attempt_id": attempt_id,
                "quiz_id": quiz_id,
                "user_id": user_id,
                "answers": answers,
                "results": results,
                "total_points": total_points,
                "earned_points": earned_points,
                "score_percentage": (earned_points / total_points * 100) if total_points > 0 else 0,
                "submitted_at": datetime.now().isoformat()
            }
            
            attempt_key = f"attempt:{attempt_id}"
            self.client.set(attempt_key, json.dumps(attempt_data))
            
            # Add to user's attempts index
            user_attempts_key = f"user_attempts:{user_id}"
            self.client.sadd(user_attempts_key, attempt_id)
            
            logger.info(f"Quiz attempt submitted: {attempt_id}")
            return attempt_data
            
        except Exception as e:
            logger.error(f"Error submitting quiz attempt: {e}")
            return None

    def get_quiz_attempt(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz attempt results"""
        if not self.client:
            logger.error("Redis client not available")
            return None
            
        try:
            attempt_key = f"attempt:{attempt_id}"
            attempt_data = self.client.get(attempt_key)
            
            if attempt_data:
                return json.loads(attempt_data)
            else:
                logger.info(f"Attempt not found: {attempt_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving attempt: {e}")
            return None

    def get_user_attempts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all quiz attempts for a user"""
        if not self.client:
            logger.error("Redis client not available")
            return []
            
        try:
            user_attempts_key = f"user_attempts:{user_id}"
            attempt_ids = self.client.smembers(user_attempts_key)
            
            attempts = []
            for attempt_id in attempt_ids:
                attempt = self.get_quiz_attempt(attempt_id)
                if attempt:
                    attempts.append(attempt)
            
            # Sort by submission time (newest first)
            attempts.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
            return attempts
            
        except Exception as e:
            logger.error(f"Error retrieving user attempts: {e}")
            return []

    def list_quizzes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all available quizzes"""
        if not self.client:
            logger.error("Redis client not available")
            return []
            
        try:
            quiz_ids = self.client.smembers("quiz_index")
            quizzes = []
            
            for quiz_id in list(quiz_ids)[:limit]:
                quiz = self.get_quiz(quiz_id)
                if quiz:
                    # Return summary info only
                    quiz_summary = {
                        "quiz_id": quiz.get("quiz_id"),
                        "title": quiz.get("title"),
                        "description": quiz.get("description"),
                        "created_at": quiz.get("created_at"),
                        "created_by": quiz.get("created_by"),
                        "question_count": len(quiz.get("questions", [])),
                        "total_points": sum(q.get("points", 1) for q in quiz.get("questions", [])),
                        "time_limit": quiz.get("time_limit"),
                        "allow_multiple_attempts": quiz.get("allow_multiple_attempts", True),
                        "shuffle_questions": quiz.get("shuffle_questions", False)
                    }
                    quizzes.append(quiz_summary)
            
            # Sort by creation time (newest first)
            quizzes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return quizzes
            
        except Exception as e:
            logger.error(f"Error listing quizzes: {e}")
            return []

    def delete_quiz(self, quiz_id: str) -> bool:
        """Delete a quiz"""
        if not self.client:
            logger.error("Redis client not available")
            return False
            
        try:
            quiz_key = f"quiz:{quiz_id}"
            
            # Remove from index
            self.client.srem("quiz_index", quiz_id)
            
            # Delete quiz data
            self.client.delete(quiz_key)
            
            logger.info(f"Deleted quiz: {quiz_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting quiz: {e}")
            return False

    def validate_answer(self, quiz_id: str, question_id: str, user_answer: Any) -> Dict[str, Any]:
        """Validate a single answer"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}
            
        # Find the question
        question = None
        for q in quiz.get("questions", []):
            if q.get("question_id") == question_id:
                question = q
                break
                
        if not question:
            return {"error": "Question not found"}
            
        correct_answer = question.get("correct_answer")
        question_type = question.get("question_type")
        
        is_correct = False
        if question_type == "multiple_choice":
            is_correct = user_answer == correct_answer
        elif question_type == "true_false":
            is_correct = user_answer == correct_answer
        elif question_type == "text":
            is_correct = str(user_answer).lower().strip() == str(correct_answer).lower().strip()
            
        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "user_answer": user_answer,
            "points": question.get("points", 1) if is_correct else 0
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize the quiz service
    quiz_service = QuizService()
    
    # Sample quiz data
    sample_quiz = {
        "title": "Python Basics Quiz",
        "description": "Test your knowledge of Python fundamentals",
        "created_by": "instructor_123",
        "questions": [
            {
                "question_id": "q1",
                "question_text": "What is the output of print(2 + 3)?",
                "question_type": "multiple_choice",
                "options": ["4", "5", "6", "7"],
                "correct_answer": "5",
                "points": 1
            },
            {
                "question_id": "q2",
                "question_text": "Python is a compiled language.",
                "question_type": "true_false",
                "correct_answer": False,
                "points": 1
            },
            {
                "question_id": "q3",
                "question_text": "What keyword is used to define a function in Python?",
                "question_type": "text",
                "correct_answer": "def",
                "points": 2
            }
        ]
    }
    
    # Test creating quiz
    quiz_id = quiz_service.create_quiz(sample_quiz)
    if quiz_id:
        print(f"✅ Quiz created successfully with ID: {quiz_id}")
        
        # Test getting quiz questions
        questions = quiz_service.get_quiz_questions(quiz_id)
        if questions:
            print(f"✅ Retrieved {len(questions)} questions for quiz")
            
        # Test submitting answers
        sample_answers = [
            {"question_id": "q1", "answer": "5"},
            {"question_id": "q2", "answer": False},
            {"question_id": "q3", "answer": "def"}
        ]
        
        attempt = quiz_service.submit_quiz_attempt(quiz_id, "user_123", sample_answers)
        if attempt:
            print(f"✅ Quiz attempt submitted. Score: {attempt['score_percentage']:.1f}%")
            
        # Test listing quizzes
        quizzes = quiz_service.list_quizzes()
        print(f"✅ Found {len(quizzes)} quizzes")
    else:
        print("❌ Failed to create quiz")