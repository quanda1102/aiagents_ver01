from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LessonRequest(BaseModel):
    subject: str
    grade: str
    lesson: str
    reference_text: str
    number_of_periods: int
    minutes_per_period: int
    special_instructions: Optional[str] = None
    example: Optional[str] = None


class Activity(BaseModel):
    name: str
    goals: str
    content: str
    products: str
    table: List[Dict[str, str]]


class LectureOutput(BaseModel):
    title: str
    goals: str
    equipment: str
    activities: List[Activity]