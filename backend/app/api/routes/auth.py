from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.api.deps import get_db, get_locale, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, Token, ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, MeResponse
from app.services.auth_service import (
    authenticate_user, create_user, generate_tokens, refresh_access_token,
    generate_email_token, verify_email_token, generate_password_reset_token, verify_password_reset_token,
    generate_2fa_secret, verify_2fa_code, create_2fa_email_code, verify_2fa_email_code
)
from app.models.user import User
from app.services.email_service import send_email

router = APIRouter()

@router.post('/register', response_model=MeResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"en": "User already exists", "fa": "کاربر قبلا وجود دارد"}[locale])
    user = create_user(db, payload.email, payload.password, payload.name)
    return user

@router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    # OAuth2PasswordRequestForm uses username field for email
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail={"en": "Invalid credentials", "fa": "اطلاعات ورود نادرست است"}[locale])
    # If 2FA enabled
    if user.two_fa_enabled:
        # prefer TOTP if secret present
        if user.two_fa_secret:
            return {"2fa_required": True, "method": "totp", "user_id": user.id}
        else:
            # create email code
            create_2fa_email_code(db, user)
            return {"2fa_required": True, "method": "email", "user_id": user.id}
    access_token, refresh_token = generate_tokens(db, user)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post('/refresh', response_model=Token)
def refresh(payload: dict, db: Session = Depends(get_db)):
    refresh_token = payload.get('refresh_token')
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    result = refresh_access_token(db, refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access, new_refresh = result
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post('/verify-email')
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user_id = verify_email_token(payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return {"ok": True}

@router.post('/forgot-password')
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # don't reveal
        return {"ok": True}
    token = generate_password_reset_token(user.id)
    send_email(user.email, 'Password Reset', f'Use this token to reset your password: {token}')
    return {"ok": True}

@router.post('/reset-password')
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_id = verify_password_reset_token(payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"ok": True}

@router.get('/me', response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Not authenticated')
    return current_user

@router.post('/verify-2fa')
def verify_2fa(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get('user_id')
    code = payload.get('code')
    if not user_id or not code:
        raise HTTPException(status_code=400, detail='user_id and code required')
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.two_fa_enabled:
        raise HTTPException(status_code=400, detail='2FA not enabled')
    # check TOTP
    ok = False
    if user.two_fa_secret:
        ok = verify_2fa_code(user.two_fa_secret, code)
    if not ok:
        # check email code
        ok = verify_2fa_email_code(db, user, code)
    if not ok:
        raise HTTPException(status_code=401, detail='Invalid 2FA code')
    # generate tokens
    access_token, refresh_token = generate_tokens(db, user)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
