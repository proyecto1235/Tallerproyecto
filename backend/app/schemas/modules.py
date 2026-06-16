from pydantic import BaseModel
from typing import Optional


class ModuleCreate(BaseModel):
    title: str
    description: str
    order: int = 0
    is_published: bool = False


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None
    difficulty: Optional[str] = None
    theory_content: Optional[str] = None


class ModuleComplete(BaseModel):
    module_id: int


class LessonComplete(BaseModel):
    module_id: int
    lesson_id: int
