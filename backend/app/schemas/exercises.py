from pydantic import BaseModel
from typing import Optional


class ExecuteRequest(BaseModel):
    code: str


class ExerciseSubmit(BaseModel):
    exercise_id: int
    code: str
    module_id: int
    is_class_exercise: bool = False
    class_module_id: Optional[int] = None
