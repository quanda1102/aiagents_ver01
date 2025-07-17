from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import uuid


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    TEXT = "text"
    ESSAY = "essay"


class QuizQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str = Field(..., min_length=1, max_length=1000)
    question_type: QuestionType
    options: Optional[List[str]] = Field(default=None, max_items=10)
    correct_answer: Union[str, bool, int] = Field(...)
    points: int = Field(default=1, ge=1, le=100)
    explanation: Optional[str] = Field(default=None, max_length=500)
    
    @field_validator('options')
    def validate_options(cls, v, info):
        question_type = info.data.get('question_type')
        if question_type == QuestionType.MULTIPLE_CHOICE:
            if not v or len(v) < 2:
                raise ValueError("Multiple choice questions must have at least 2 options")
        elif question_type == QuestionType.TRUE_FALSE:
            if v is not None:
                raise ValueError("True/false questions should not have options")
        return v
    
    @field_validator('correct_answer')
    def validate_correct_answer(cls, v, info):
        question_type = info.data.get('question_type')
        if question_type == QuestionType.TRUE_FALSE:
            if not isinstance(v, bool):
                raise ValueError("True/false questions must have boolean correct_answer")
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            options = info.data.get('options', [])
            if isinstance(v, str) and v not in options:
                raise ValueError("Correct answer must be one of the provided options")
        return v


class CreateQuizRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    questions: List[QuizQuestion] = Field(..., min_items=1, max_items=100)
    created_by: Optional[str] = Field(default=None, min_length=1, max_length=100)
    time_limit: Optional[int] = Field(default=None, ge=1, le=10800)  # Max 3 hours in seconds
    allow_multiple_attempts: bool = Field(default=True)
    shuffle_questions: bool = Field(default=False)
    
    @field_validator('questions')
    def validate_questions(cls, v):
        if len(v) == 0:
            raise ValueError("Quiz must have at least one question")
        return v


class QuizSummary(BaseModel):
    quiz_id: str
    title: str
    description: Optional[str]
    created_at: str
    created_by: str
    question_count: int
    total_points: int
    time_limit: Optional[int]
    allow_multiple_attempts: bool
    shuffle_questions: bool
    class_code: Optional[str] = None


class QuizForTaking(BaseModel):
    quiz_id: str
    title: str
    description: Optional[str]
    questions: List[Dict[str, Any]]  # Questions without correct answers
    total_points: int
    time_limit: Optional[int]
    allow_multiple_attempts: bool
    shuffle_questions: bool


class QuizAnswer(BaseModel):
    question_id: str
    answer: Union[str, bool, int, List[str]]
    
    @field_validator('answer')
    def validate_answer(cls, v):
        if isinstance(v, str) and len(v.strip()) == 0:
            raise ValueError("Text answers cannot be empty")
        return v


class SubmitQuizRequest(BaseModel):
    quiz_id: str
    user_id: str
    answers: List[QuizAnswer] = Field(..., min_items=1)
    
    @field_validator('answers')
    def validate_answers(cls, v):
        question_ids = [answer.question_id for answer in v]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Duplicate question IDs found in answers")
        return v


class QuizResult(BaseModel):
    question_id: str
    user_answer: Union[str, bool, int, List[str]]
    correct_answer: Union[str, bool, int, List[str]]
    is_correct: bool
    points: int
    explanation: Optional[str] = None


class QuizAttempt(BaseModel):
    attempt_id: str
    quiz_id: str
    user_id: str
    answers: List[QuizAnswer]
    results: List[QuizResult]
    total_points: int
    earned_points: int
    score_percentage: float
    submitted_at: str

class QuizAttemptWithInfo(BaseModel):
    attempt_id: str
    quiz_id: str
    quiz_title: Optional[str] = None
    quiz_class_code: Optional[str] = None
    user_id: str
    answers: List[QuizAnswer]
    results: List[QuizResult]
    total_points: int
    earned_points: int
    score_percentage: float
    submitted_at: str


class ValidateAnswerRequest(BaseModel):
    quiz_id: str
    question_id: str
    user_answer: Union[str, bool, int, List[str]]


class ValidateAnswerResponse(BaseModel):
    question_id: str
    is_correct: bool
    correct_answer: Union[str, bool, int, List[str]]
    user_answer: Union[str, bool, int, List[str]]
    points: int
    explanation: Optional[str] = None


class GenerateQuizRequest(BaseModel):
    document_text: str = Field(..., min_length=1, max_length=50000)
    quiz_title: Optional[str] = Field(default=None, max_length=200)
    number_of_questions: int = Field(default=5, ge=1, le=20)
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_types: List[QuestionType] = Field(default=[QuestionType.MULTIPLE_CHOICE])
    created_by: Optional[str] = Field(default=None, min_length=1, max_length=100)
    
    @field_validator('question_types')
    def validate_question_types(cls, v):
        if len(v) == 0:
            raise ValueError("At least one question type must be specified")
        return v


class GenerateQuizResponse(BaseModel):
    quiz_id: str
    message: str
    quiz_summary: QuizSummary


class QuizListResponse(BaseModel):
    quizzes: List[QuizSummary]
    total_count: int


class QuizResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class UserQuizStats(BaseModel):
    user_id: str
    total_attempts: int
    average_score: float
    best_score: float
    quizzes_taken: int
    recent_attempts: List[QuizAttemptWithInfo]