from typing import List, Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class TeacherRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User:
    def __init__(
        self,
        id: Optional[int],
        email: str,
        password_hash: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        is_active: bool = True,
        teacher_request_status: Optional[TeacherRequestStatus] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.teacher_request_status = teacher_request_status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "teacher_request_status": self.teacher_request_status.value if self.teacher_request_status else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
