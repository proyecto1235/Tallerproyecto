from pydantic import BaseModel
from typing import Optional


class ChallengeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: int = 1
    points: int = 100
    base_code: Optional[str] = ""
    solution_code: Optional[str] = None
    solution_type: str = "output"
    solution_output: Optional[str] = None
    test_code: Optional[str] = None
    deadline: Optional[str] = None
    is_published: bool = False
    max_attempts: int = 0


class ChallengeSubmit(BaseModel):
    challenge_id: int
    code: str
