from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: Optional[str]
    type: str = 'info'

class NotificationCreate(NotificationBase):
    user_id: Optional[int]

class NotificationRead(NotificationBase):
    id: int
    read: bool
    user_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
