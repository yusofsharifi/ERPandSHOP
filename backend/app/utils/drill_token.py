from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings

ALGORITHM = "HS256"


def generate_drill_token(payload: Dict[str, Any], expires_seconds: int = 300) -> str:
    now = datetime.utcnow()
    data = payload.copy()
    data.update({"exp": now + timedelta(seconds=expires_seconds), "iat": now})
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_drill_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # remove iat/exp from payload
        data.pop('iat', None)
        data.pop('exp', None)
        return data
    except JWTError:
        return None
