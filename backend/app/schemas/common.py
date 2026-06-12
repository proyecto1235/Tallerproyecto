from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenData(BaseModel):
    user_id: int
    email: str
    role: str
    exp: datetime
    jti: Optional[str] = None
