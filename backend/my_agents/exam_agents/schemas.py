"""
Pydantic schemas for the multi-agent examination system
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from schemas.quiz_models import QuestionType, QuizQuestion


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ExamFormat(str, Enum):
    ACADEMIC = "academic"
    PROFESSIONAL = "professional" 
    CERTIFICATION = "certification"
    PRACTICE = "practice"


class ExaminationRequest(BaseModel):
    """Request model for creating an examination"""
    subject: str = Field(..., min_length=1, max_length=200, description="Subject or topic of the examination")
    description: Optional[str] = Field(default=None, max_length=1000, description="Detailed description of exam content")
    number_of_questions: int = Field(default=10, ge=1, le=50, description="Total number of questions")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Overall difficulty level")
    exam_format: ExamFormat = Field(default=ExamFormat.ACADEMIC, description="Type of examination format")
    question_types: List[QuestionType] = Field(default=[QuestionType.MULTIPLE_CHOICE], description="Types of questions to include")
    time_limit: Optional[int] = Field(default=None, ge=1, le=10800, description="Time limit in seconds")
    context_material: Optional[str] = Field(default=None, max_length=10000, description="Reference material or context for the exam")
    learning_objectives: Optional[List[str]] = Field(default=None, description="Specific learning objectives to assess")


class ExamFormatSpec(BaseModel):
    """Specification for exam format and structure"""
    exam_title: str = Field(..., description="Title of the examination")
    instructions: str = Field(..., description="Instructions for taking the exam")
    sections: List[Dict[str, Any]] = Field(default_factory=list, description="Exam sections with their specifications")
    grading_criteria: Dict[str, Any] = Field(default_factory=dict, description="Grading criteria and rubrics")
    question_distribution: Dict[QuestionType, int] = Field(default_factory=dict, description="Distribution of question types")


class QuestionSpec(BaseModel):
    """Specification for a single question"""
    topic: str = Field(..., description="Topic or subtopic for the question")
    question_type: QuestionType = Field(..., description="Type of question")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level of the question")
    points: int = Field(default=1, ge=1, le=10, description="Points assigned to the question")
    learning_objective: Optional[str] = Field(default=None, description="Specific learning objective this question assesses")
    bloom_taxonomy_level: Optional[str] = Field(default=None, description="Bloom's taxonomy level (remember, understand, apply, analyze, evaluate, create)")


class GeneratedQuestion(BaseModel):
    """A generated question with metadata"""
    question: QuizQuestion = Field(..., description="The generated question")
    spec: QuestionSpec = Field(..., description="The specification used to generate this question")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality assessment score")
    feedback: Optional[str] = Field(default=None, description="Quality feedback or suggestions")


class ExamQualityAssessment(BaseModel):
    """Quality assessment of the entire examination"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    question_scores: List[float] = Field(..., description="Individual question quality scores")
    coverage_analysis: Dict[str, Any] = Field(default_factory=dict, description="Analysis of topic coverage")
    difficulty_distribution: Dict[DifficultyLevel, int] = Field(default_factory=dict, description="Distribution of difficulty levels")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    issues: List[str] = Field(default_factory=list, description="Identified issues or problems")


class ExamGenerationResult(BaseModel):
    """Final result of the exam generation process"""
    exam_id: str = Field(..., description="Generated exam identifier")
    title: str = Field(..., description="Exam title")
    format_spec: ExamFormatSpec = Field(..., description="Exam format specification")
    questions: List[GeneratedQuestion] = Field(..., description="Generated questions with metadata")
    quality_assessment: ExamQualityAssessment = Field(..., description="Quality assessment of the exam")
    total_points: int = Field(..., description="Total points for the exam")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    created_by: str = Field(..., description="Email of the user who created the exam")