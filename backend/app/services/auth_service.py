import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import pyotp

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.login_attempt import LoginAttempt
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.services.email_service import send_email

ACCESS_EXPIRE_MIN = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_user(db: Session, email: str, password: str, name: Optional[str] = None) -> User:
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    # send verification email
    token = generate_email_token(user.id)
    send_email(user.email, "Verify your email", f"Use this token to verify: {token}")
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    attempt = LoginAttempt(email=email, user_id=user.id if user else None, ip_address=None, user_agent=None)
    if not user:
        attempt.success = False
        db.add(attempt)
        db.commit()
        return None
    if not verify_password(password, user.hashed_password):
        attempt.success = False
        db.add(attempt)
        db.commit()
        return None
    attempt.success = True
    db.add(attempt)
    db.commit()
    return user

def generate_tokens(db: Session, user: User):
    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=ACCESS_EXPIRE_MIN))
    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    rt = RefreshToken(token=refresh_token, user_id=user.id, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return access_token, refresh_token

def refresh_access_token(db: Session, refresh_token: str) -> Optional[tuple]:
    # Rotate refresh token: revoke old and issue new refresh + access
    rt = db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.revoked == False).first()
    if not rt:
        return None
    if rt.expires_at and rt.expires_at < datetime.utcnow():
        return None
    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user:
        return None
    # revoke old
    rt.revoked = True
    db.add(rt)
    # create new refresh token
    new_refresh = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    new_rt = RefreshToken(token=new_refresh, user_id=user.id, expires_at=expires_at)
    db.add(new_rt)
    db.commit()
    db.refresh(new_rt)
    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=ACCESS_EXPIRE_MIN))
    return access_token, new_refresh

# Two-factor email codes
from datetime import timedelta as _td
from app.models.two_fa_code import TwoFACode
import random

def create_2fa_email_code(db: Session, user: User, ttl_minutes: int = 10) -> TwoFACode:
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + _td(minutes=ttl_minutes)
    t = TwoFACode(user_id=user.id, code=code, expires_at=expires_at)
    db.add(t)
    db.commit()
    db.refresh(t)
    # send via email
    send_email(user.email, 'Your 2FA code', f'Your verification code is: {code}')
    return t

def verify_2fa_email_code(db: Session, user: User, code: str) -> bool:
    t = db.query(TwoFACode).filter(TwoFACode.user_id == user.id, TwoFACode.code == code, TwoFACode.used == False).order_by(TwoFACode.created_at.desc()).first()
    if not t:
        return False
    if t.expires_at < datetime.utcnow():
        return False
    t.used = True
    db.add(t)
    db.commit()
    return True

# Email verification / password reset through JWT tokens
from jose import jwt

def generate_email_token(user_id: int, expires_hours: int = 48) -> str:
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "email_verification"}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def verify_email_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get('type') != 'email_verification':
            return None
        return int(payload.get('sub'))
    except Exception:
        return None

def generate_password_reset_token(user_id: int, expires_hours: int = 2) -> str:
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "password_reset"}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def verify_password_reset_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get('type') != 'password_reset':
            return None
        return int(payload.get('sub'))
    except Exception:
        return None

# 2FA helpers using pyotp

def generate_2fa_secret() -> str:
    return pyotp.random_base32()

def verify_2fa_code(secret: str, code: str) -> bool:
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    except Exception:
        return False
