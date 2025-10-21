from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    otp: Optional[str] = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str]

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str

class MeResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True
