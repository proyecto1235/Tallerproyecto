from pydantic import BaseModel
from typing import Optional


class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None
    invite_code: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    invite_code: Optional[str] = None
    is_active: Optional[bool] = None


class ClassStudentAdd(BaseModel):
    student_public_id: str


class ClassModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    theory_content: Optional[str] = None
    order: int = 0


class ClassModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    theory_content: Optional[str] = None
    order: Optional[int] = None


class ClassExerciseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    exercise_type: str = "coding"
    difficulty: int = 1
    points: int = 10
    order: int = 0
    solution_output: Optional[str] = None
    solution_type: Optional[str] = "output"
    test_code: Optional[str] = None
    metadata: Optional[dict] = None


class ClassExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    exercise_type: Optional[str] = None
    difficulty: Optional[int] = None
    points: Optional[int] = None
    order: Optional[int] = None
    solution_output: Optional[str] = None
    solution_type: Optional[str] = None
    test_code: Optional[str] = None
    metadata: Optional[dict] = None
