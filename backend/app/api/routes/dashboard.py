from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from app.api.deps import get_db, get_current_user, role_required
from app.services.statistics_service import get_dashboard_stats
from app.core.config import settings

# optional redis
redis_client = None
try:
    import redis
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
except Exception:
    redis_client = None

router = APIRouter()

CACHE_PREFIX = 'dashboard:stats:'

def cache_get(key: str):
    if not redis_client:
        return None
    try:
        v = redis_client.get(key)
        return json.loads(v) if v else None
    except Exception:
        return None

def cache_set(key: str, value, expire: int = 60):
    if not redis_client:
        return
    try:
        redis_client.setex(key, expire, json.dumps(value))
    except Exception:
        pass

@router.get('/', dependencies=[Depends(role_required('Admin'))])
def dashboard_stats(start: Optional[str] = Query(None), end: Optional[str] = Query(None), db: Session = Depends(get_db)):
    # parse dates
    start_dt = None
    end_dt = None
    key_part = 'all'
    try:
        if start:
            start_dt = datetime.fromisoformat(start)
        if end:
            end_dt = datetime.fromisoformat(end)
        if start_dt or end_dt:
            key_part = f"{start or ''}:{end or ''}"
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid date format; use ISO format YYYY-MM-DDTHH:MM:SS')

    cache_key = CACHE_PREFIX + key_part
    cached = cache_get(cache_key)
    if cached:
        return cached

    stats = get_dashboard_stats(db, start_dt, end_dt)
    cache_set(cache_key, stats, expire=60)
    return stats
