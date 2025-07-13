from __future__ import annotations

import asyncio
import json
import uuid
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from agents import Agent, Runner
from pydantic import BaseModel, Field

from services.quiz_service import QuizService
from schemas.quiz_models import QuestionType, QuizQuestion as StandardQuizQuestion
# ---------------------------------------------------------------------------
# 1. Define the structured output of the agent using `pydantic`.
# ---------------------------------------------------------------------------

class QuizQuestion(BaseModel):
    """A single quiz question with its metadata - for AI generation output."""
    
    question_text: str = Field(description="The actual question text")
    question_type: QuestionType = Field(description="Type of question: multiple_choice, true_false, text, or essay")
    options: Optional[List[str]] = Field(None, description="Options for multiple choice questions")
    correct_answer: Union[str, bool, int] = Field(description="The correct answer - string for text/multiple choice, boolean for true/false")
    points: int = Field(default=1, description="Points awarded for correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of the correct answer")


class QuizGenerationOutput(BaseModel):
    """Structured output for quiz generation."""
    
    title: str = Field(description="Title of the generated quiz")
    description: str = Field(description="Description of the quiz")
    questions: List[QuizQuestion] = Field(description="List of generated questions")
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    allow_multiple_attempts: bool = Field(default=True, description="Whether to allow multiple attempts")
    shuffle_questions: bool = Field(default=True, description="Whether to shuffle questions")


# ---------------------------------------------------------------------------
# 2. Create the agent, give it instructions, an output type and model.
# ---------------------------------------------------------------------------

QUIZ_GENERATION_AGENT = Agent(
    name="QuizGenerationAgent",
    instructions=(
        "You are an expert quiz generator. Your task is to create comprehensive, educational quizzes from provided documents.\n\n"
        "Guidelines:\n"
        "1. Read the document carefully and identify key concepts, facts, and learning objectives\n"
        "2. Create questions that test understanding at different levels (factual, conceptual, analytical)\n"
        "3. Ensure questions are clear, unambiguous, and have definitive correct answers\n"
        "4. For multiple choice questions, create 3-4 plausible options with only one correct answer\n"
        "5. Balance different question types based on the content\n"
        "6. Assign appropriate point values based on question difficulty (1-3 points)\n"
        "7. Include brief explanations for correct answers when helpful\n\n"
        "Question Types Available:\n"
        "- multiple_choice: 3-4 options, one correct answer\n"
        "- true_false: Boolean questions with clear true/false answers\n"
        "- text: Short answer questions requiring specific text responses\n"
        "- essay: Open-ended questions (use sparingly)\n\n"
        "For difficulty levels:\n"
        "- easy: 1 point, basic recall questions\n"
        "- medium: 2 points, comprehension and application questions\n"
        "- hard: 3 points, analysis and evaluation questions\n\n"
        "Ensure the quiz covers the main topics in the document comprehensively."
    ),
    output_type=QuizGenerationOutput,
    model="gpt-4o-mini",
)


# ---------------------------------------------------------------------------
# 3. Quiz Generation Agent Class
# ---------------------------------------------------------------------------

class QuizGenerationAgent:
    def __init__(self):
        self.name = "QuizGenerationAgent"
        self.role = "AI-powered quiz generation from documents"
        self.quiz_service = QuizService()

    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process quiz generation request"""
        try:
            document_text = input_data.get("document_text", "")
            quiz_title = input_data.get("quiz_title", "Generated Quiz")
            number_of_questions = input_data.get("number_of_questions", 5)
            difficulty_level = input_data.get("difficulty_level", "medium")
            question_types = input_data.get("question_types", ["multiple_choice"])
            created_by = input_data.get("created_by", "AI Agent")
            
            if not document_text:
                return {"error": "Document text is required"}
            
            # Prepare the prompt for the AI agent
            prompt = self._create_generation_prompt(
                document_text, quiz_title, number_of_questions, 
                difficulty_level, question_types
            )
            
            # Run the quiz generation agent
            result = await Runner.run(QUIZ_GENERATION_AGENT, prompt)
            quiz_data = result.final_output_as(QuizGenerationOutput)
            
            # Convert to dictionary and add metadata
            quiz_dict = quiz_data.model_dump()
            quiz_dict["created_by"] = created_by
            
            # Convert questions to the format expected by QuizService (using proper UUID generation)
            formatted_questions = []
            for q in quiz_dict["questions"]:
                # Create a proper QuizQuestion with UUID
                standard_question = StandardQuizQuestion(
                    question_text=q["question_text"],
                    question_type=q["question_type"],
                    options=q.get("options"),
                    correct_answer=q["correct_answer"],
                    points=q.get("points", 1),
                    explanation=q.get("explanation")
                )
                formatted_questions.append(standard_question.model_dump())
            
            quiz_dict["questions"] = formatted_questions
            
            # Create the quiz in the database
            quiz_id = self.quiz_service.create_quiz(quiz_dict)
            
            if not quiz_id:
                return {"error": "Failed to save generated quiz"}
            
            return {
                "quiz_id": quiz_id,
                "message": "Quiz generated successfully",
                "quiz_data": quiz_dict
            }
            
        except Exception as e:
            return {"error": f"Error generating quiz: {str(e)}"}

    def _create_generation_prompt(
        self, 
        document_text: str, 
        quiz_title: str, 
        number_of_questions: int,
        difficulty_level: str,
        question_types: List[str]
    ) -> str:
        """Create a detailed prompt for the AI agent"""
        
        question_types_str = ", ".join(question_types)
        
        prompt = f"""
Generate a quiz from the following document:

DOCUMENT:
{document_text}

REQUIREMENTS:
- Quiz Title: {quiz_title}
- Number of Questions: {number_of_questions}
- Difficulty Level: {difficulty_level}
- Question Types to Include: {question_types_str}

Please create a comprehensive quiz that covers the key concepts from the document. 
Ensure questions are well-distributed across different difficulty levels and question types.
Make sure each question has a clear, unambiguous correct answer.

For multiple choice questions, provide 3-4 plausible options.
For true/false questions, ensure the statement can be definitively classified as true or false.
For text questions, the correct answer should be a specific word or short phrase.

The quiz should help assess understanding of the main topics and concepts presented in the document.
"""
        
        return prompt


# ---------------------------------------------------------------------------
# 4. Testing function
# ---------------------------------------------------------------------------

async def test_quiz_generation():
    """Test the quiz generation agent"""
    agent = QuizGenerationAgent()
    
    sample_document = """
    Python is a high-level programming language created by Guido van Rossum and first released in 1991. 
    It is known for its simplicity and readability, making it an excellent choice for beginners. 
    Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.
    
    Key features of Python include:
    - Dynamic typing: Variables don't need explicit type declarations
    - Interpreted language: Code is executed line by line
    - Extensive standard library: Many built-in modules and functions
    - Cross-platform compatibility: Runs on Windows, macOS, and Linux
    
    Python is widely used in web development, data science, artificial intelligence, automation, and scientific computing.
    Popular frameworks include Django and Flask for web development, and libraries like NumPy and Pandas for data analysis.
    """
    
    input_data = {
        "document_text": sample_document,
        "quiz_title": "Python Programming Basics",
        "number_of_questions": 5,
        "difficulty_level": "medium",
        "question_types": ["multiple_choice", "true_false", "text"],
        "created_by": "Test Agent"
    }
    
    result = await agent.process(input_data, {})
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_quiz_generation())