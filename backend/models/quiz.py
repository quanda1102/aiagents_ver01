from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(String(255), unique=True, index=True)  # UUID string
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(JSON, nullable=False)  # Store questions as JSON
    created_by = Column(String(255), nullable=False)  # Email of creator
    created_at = Column(DateTime, default=datetime.utcnow)
    time_limit = Column(Integer, nullable=True)  # In minutes
    allow_multiple_attempts = Column(Boolean, default=True)
    shuffle_questions = Column(Boolean, default=False)
    class_code = Column(String(100), nullable=True)  # Assigned to class
    
    # Relationships
    attempts = relationship("QuizAttempt", back_populates="quiz")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(String(255), unique=True, index=True)  # UUID string
    quiz_id = Column(String(255), ForeignKey("quizzes.quiz_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answers = Column(JSON, nullable=False)  # User's submitted answers
    results = Column(JSON, nullable=False)  # Detailed results per question
    total_points = Column(Integer, nullable=False)
    earned_points = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")