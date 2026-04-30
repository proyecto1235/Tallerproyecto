from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AlertType(Enum):
    DIFFICULTY = "difficulty"
    SLOW_LEARNER = "slow_learner"
    FAST_LEARNER = "fast_learner"

class AlertPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Alert(BaseModel):
    id: Optional[str] = None
    teacher_id: int
    student_id: Optional[int] = None
    module_id: Optional[int] = None
    type: AlertType
    priority: AlertPriority
    message: str
    recommendations: List[str]
    created_at: str
    student_name: Optional[str] = None
    module_name: Optional[str] = None
