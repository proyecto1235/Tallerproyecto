from typing import Optional, List
from datetime import datetime
from enum import Enum

class ContentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_DELETION = "pending_deletion"

class Module:
    def __init__(
        self,
        id: Optional[int],
        title: str,
        description: str,
        teacher_id: int,
        status: ContentStatus = ContentStatus.DRAFT,
        order: int = 0,
        is_published: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.teacher_id = teacher_id
        self.status = status
        self.order = order
        self.is_published = is_published
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "teacher_id": self.teacher_id,
            "status": self.status.value,
            "order": self.order,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
