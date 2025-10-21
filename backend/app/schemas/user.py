from pydantic import BaseModel, EmailStr
from typing import Optional, Any, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]

class UserCreate(UserBase):
    password: str
    role: Optional[str]

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    role: Optional[str]
    is_active: Optional[bool]

class UserRead(UserBase):
    id: int
    is_active: bool
    role_id: Optional[int]
    created_at: datetime
    role: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True
