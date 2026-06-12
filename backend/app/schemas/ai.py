from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    context: Optional[dict] = None


class PublicChatRequest(BaseModel):
    message: str
    session_id: str
    history: Optional[list] = []


class ExerciseGenerateRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    exercise_type: str = "coding"
    language: str = "python"
    additional_instructions: Optional[str] = None


class TutorRequest(BaseModel):
    question: str
    module_id: Optional[int] = None
    code: Optional[str] = None


class FeedbackRequest(BaseModel):
    content: str
    rating: int = 5
    module_id: Optional[int] = None
    exercise_id: Optional[int] = None
    category: Optional[str] = None


class ExerciseSuggestionRequest(BaseModel):
    exercise_id: int
    title: str
    description: str
    instructions: str
    solution: str
    difficulty: int


class RAGIndexRequest(BaseModel):
    text: str
    source_type: str
    source_id: int
    metadata: Optional[dict] = None


class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_type: Optional[str] = None


class AITutorAskRequest(BaseModel):
    message: str
    student_level: str = "beginner"


class TutorAskRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    exercise_id: Optional[int] = None
    module_id: Optional[int] = None
    history: Optional[list] = []


class TutorHintRequest(BaseModel):
    exercise_id: int
    module_id: Optional[int] = None


class TutorExplainRequest(BaseModel):
    concept: str
    module_id: Optional[int] = None


class AnalyticsFilter(BaseModel):
    module_id: Optional[int] = None
    days: int = 30
