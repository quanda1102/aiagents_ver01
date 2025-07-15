from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from config import config
from models.quiz import Quiz, QuizAttempt
from models.user import User
from models import Base
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class MySQLQuizService:
    def __init__(self):
        """Initialize the MySQL Quiz Service"""
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        logger.info("MySQLQuizService initialized with database connection")

    def get_db(self):
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e

    def create_quiz(self, quiz_data: Dict[str, Any]) -> Optional[str]:
        """Create a new quiz and return quiz_id"""
        db = self.get_db()
        try:
            quiz_id = str(uuid.uuid4())
            
            # Extract quiz metadata
            quiz = Quiz(
                quiz_id=quiz_id,
                title=quiz_data.get("title"),
                description=quiz_data.get("description"),
                questions=quiz_data.get("questions", []),
                created_by=quiz_data.get("created_by", "anonymous"),
                created_at=datetime.utcnow(),
                time_limit=quiz_data.get("time_limit"),
                allow_multiple_attempts=quiz_data.get("allow_multiple_attempts", True),
                shuffle_questions=quiz_data.get("shuffle_questions", False),
                class_code=quiz_data.get("class_code")  # For teacher assignment
            )
            
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            
            logger.info(f"Created quiz with ID: {quiz_id}")
            return quiz_id
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating quiz: {e}")
            return None
        finally:
            db.close()

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz by ID"""
        db = self.get_db()
        try:
            quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            
            if quiz:
                return {
                    "quiz_id": quiz.quiz_id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "questions": quiz.questions,
                    "created_by": quiz.created_by,
                    "created_at": quiz.created_at.isoformat(),
                    "time_limit": quiz.time_limit,
                    "allow_multiple_attempts": quiz.allow_multiple_attempts,
                    "shuffle_questions": quiz.shuffle_questions,
                    "class_code": quiz.class_code
                }
            else:
                logger.info(f"Quiz not found: {quiz_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving quiz: {e}")
            return None
        finally:
            db.close()

    def get_quiz_questions(self, quiz_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get quiz questions without answers (for taking quiz)"""
        quiz_data = self.get_quiz(quiz_id)
        if not quiz_data:
            return None
            
        # Remove correct answers from questions
        questions = []
        for q in quiz_data.get("questions", []):
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
        db = self.get_db()
        try:
            quiz_data = self.get_quiz(quiz_id)
            if not quiz_data:
                return None
                
            # Calculate score
            total_points = 0
            earned_points = 0
            results = []
            
            for question in quiz_data.get("questions", []):
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
            score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
            
            # Get user ID as integer - work with existing database schema
            try:
                user_id_int = int(user_id)
                # Verify user exists in database using direct SQL since User model doesn't match schema
                from sqlalchemy import text
                result = db.execute(text("SELECT id FROM users WHERE id = :user_id"), {"user_id": user_id_int})
                user_exists = result.fetchone()
                
                if not user_exists:
                    logger.error(f"User not found: {user_id}")
                    return None
                    
            except ValueError:
                logger.error(f"Invalid user ID format: {user_id}")
                return None
            
            attempt = QuizAttempt(
                attempt_id=attempt_id,
                quiz_id=quiz_id,
                user_id=user_id_int,
                answers=answers,
                results=results,
                total_points=total_points,
                earned_points=earned_points,
                score_percentage=score_percentage,
                submitted_at=datetime.utcnow()
            )
            
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
            
            attempt_data = {
                "attempt_id": attempt_id,
                "quiz_id": quiz_id,
                "user_id": str(user_id_int),
                "answers": answers,
                "results": results,
                "total_points": total_points,
                "earned_points": earned_points,
                "score_percentage": score_percentage,
                "submitted_at": attempt.submitted_at.isoformat()
            }
            
            logger.info(f"Quiz attempt submitted: {attempt_id}")
            return attempt_data
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting quiz attempt: {e}")
            return None
        finally:
            db.close()

    def get_quiz_attempt(self, attempt_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz attempt results"""
        db = self.get_db()
        try:
            attempt = db.query(QuizAttempt).filter(QuizAttempt.attempt_id == attempt_id).first()
            
            if attempt:
                return {
                    "attempt_id": attempt.attempt_id,
                    "quiz_id": attempt.quiz_id,
                    "user_id": str(attempt.user_id),
                    "answers": attempt.answers,
                    "results": attempt.results,
                    "total_points": attempt.total_points,
                    "earned_points": attempt.earned_points,
                    "score_percentage": attempt.score_percentage,
                    "submitted_at": attempt.submitted_at.isoformat()
                }
            else:
                logger.info(f"Attempt not found: {attempt_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving attempt: {e}")
            return None
        finally:
            db.close()

    def get_user_attempts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all quiz attempts for a specific user"""
        db = self.get_db()
        try:
            attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
            
            attempt_data = []
            for attempt in attempts:
                attempt_dict = {
                    "attempt_id": attempt.attempt_id,
                    "quiz_id": attempt.quiz_id,
                    "user_id": attempt.user_id,
                    "submitted_at": attempt.submitted_at.isoformat(),
                    "earned_points": attempt.earned_points,
                    "total_points": attempt.total_points,
                    "score_percentage": round((attempt.earned_points / attempt.total_points * 100), 2) if attempt.total_points > 0 else 0,
                    "results": attempt.results,
                    "is_passed": attempt.is_passed
                }
                attempt_data.append(attempt_dict)
                
            # Sort by submission time (newest first)
            attempt_data.sort(key=lambda x: x["submitted_at"], reverse=True)
            return attempt_data
            
        except Exception as e:
            logger.error(f"Error retrieving user attempts: {e}")
            return []
        finally:
            db.close()
            
    def get_all_attempts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all quiz attempts (for teachers/admins)"""
        db = self.get_db()
        try:
            attempts = db.query(QuizAttempt).order_by(QuizAttempt.submitted_at.desc()).limit(limit).all()
            
            attempt_data = []
            for attempt in attempts:
                attempt_dict = {
                    "attempt_id": attempt.attempt_id,
                    "quiz_id": attempt.quiz_id,
                    "user_id": attempt.user_id,
                    "submitted_at": attempt.submitted_at.isoformat(),
                    "earned_points": attempt.earned_points,
                    "total_points": attempt.total_points,
                    "score_percentage": round((attempt.earned_points / attempt.total_points * 100), 2) if attempt.total_points > 0 else 0,
                    "results": attempt.results,
                    "is_passed": attempt.is_passed
                }
                attempt_data.append(attempt_dict)
                
            return attempt_data
            
        except Exception as e:
            logger.error(f"Error retrieving all attempts: {e}")
            return []
        finally:
            db.close()

    def list_quizzes(self, limit: int = 50, class_code: str = None, user: User = None) -> List[Dict[str, Any]]:
        """List all available quizzes, optionally filtered by class"""
        db = self.get_db()
        try:
            query = db.query(Quiz)
            
            # Filter by class if user is a student
            if user and user.role == 3:  # STUDENT role
                query = query.filter(
                    (Quiz.class_code == user.class_name) | (Quiz.class_code.is_(None))
                )
            elif class_code:
                query = query.filter(Quiz.class_code == class_code)
            
            quizzes = query.order_by(Quiz.created_at.desc()).limit(limit).all()
            
            quiz_summaries = []
            for quiz in quizzes:
                quiz_summary = {
                    "quiz_id": quiz.quiz_id,
                    "title": quiz.title,
                    "description": quiz.description,
                    "created_at": quiz.created_at.isoformat(),
                    "created_by": quiz.created_by,
                    "question_count": len(quiz.questions) if quiz.questions else 0,
                    "total_points": sum(q.get("points", 1) for q in quiz.questions) if quiz.questions else 0,
                    "time_limit": quiz.time_limit,
                    "allow_multiple_attempts": quiz.allow_multiple_attempts,
                    "shuffle_questions": quiz.shuffle_questions,
                    "class_code": quiz.class_code
                }
                quiz_summaries.append(quiz_summary)
            
            return quiz_summaries
            
        except Exception as e:
            logger.error(f"Error listing quizzes: {e}")
            return []
        finally:
            db.close()

    def delete_quiz(self, quiz_id: str) -> bool:
        """Delete a quiz and all related attempts"""
        db = self.get_db()
        try:
            # Delete related attempts first
            db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).delete()
            
            # Delete quiz
            quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            if quiz:
                db.delete(quiz)
                db.commit()
                logger.info(f"Deleted quiz: {quiz_id}")
                return True
            else:
                logger.info(f"Quiz not found for deletion: {quiz_id}")
                return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting quiz: {e}")
            return False
        finally:
            db.close()

    def validate_answer(self, quiz_id: str, question_id: str, user_answer: Any) -> Dict[str, Any]:
        """Validate a single answer"""
        quiz_data = self.get_quiz(quiz_id)
        if not quiz_data:
            return {"error": "Quiz not found"}
            
        # Find the question
        question = None
        for q in quiz_data.get("questions", []):
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

    def assign_quiz_to_class(self, quiz_id: str, class_code: str) -> bool:
        """Assign a quiz to a specific class"""
        db = self.get_db()
        try:
            quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
            if quiz:
                quiz.class_code = class_code
                db.commit()
                logger.info(f"Assigned quiz {quiz_id} to class {class_code}")
                return True
            else:
                logger.error(f"Quiz not found: {quiz_id}")
                return False
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning quiz to class: {e}")
            return False
        finally:
            db.close()

    def get_quizzes_for_user(self, user: User) -> List[Dict[str, Any]]:
        """Get quizzes assigned to user's class"""
        if user.role == 3:  # STUDENT
            return self.list_quizzes(user=user)
        else:
            return self.list_quizzes()