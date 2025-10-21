from typing import Generator, Optional, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Database dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.user.User).filter(models.user.User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

# Helper to get locale from request headers
def get_locale(request: Request) -> str:
    accept = request.headers.get('accept-language', '')
    if accept.startswith('fa'):
        return 'fa'
    return 'en'

# Role check dependency
def role_required(role_name: str) -> Callable:
    def _check_role(current_user = Depends(get_current_user)):
        if not current_user or not current_user.role or current_user.role.name != role_name:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation requires %s role" % role_name)
        return current_user
    return _check_role
