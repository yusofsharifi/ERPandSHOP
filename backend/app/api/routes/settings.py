from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json

from app.api.deps import get_db, get_locale
from app.models.setting import Setting, SettingCategory
from app.schemas.setting import SettingRead, SettingBulkUpdate
from app.services.email_service import test_smtp
from app.core.config import settings

# Optional redis
redis_client = None
try:
    import redis
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
except Exception:
    redis_client = None

router = APIRouter()

CACHE_PREFIX = "settings:"

def cache_get(key: str):
    if not redis_client:
        return None
    try:
        v = redis_client.get(key)
        return json.loads(v) if v else None
    except Exception:
        return None

def cache_set(key: str, value: Any, expire: int = 300):
    if not redis_client:
        return
    try:
        redis_client.setex(key, expire, json.dumps(value))
    except Exception:
        pass

@router.get('/', response_model=List[SettingRead])
def list_settings(category: Optional[str] = Query(None), db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    cache_key = CACHE_PREFIX + (category or 'all') + ':' + locale
    cached = cache_get(cache_key)
    if cached:
        return cached
    q = db.query(Setting)
    if category:
        try:
            cat = SettingCategory(category)
            q = q.filter(Setting.category == cat)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid category")
    items = q.all()
    result = []
    for item in items:
        # include translation for label if exists
        obj = SettingRead.from_orm(item)
        result.append(obj)
    cache_set(cache_key, [r.dict() for r in result])
    return result

@router.get('/{key}', response_model=SettingRead)
def get_setting(key: str, db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    cache_key = CACHE_PREFIX + key + ':' + locale
    cached = cache_get(cache_key)
    if cached:
        return cached
    item = db.query(Setting).filter(Setting.key == key).first()
    if not item:
        raise HTTPException(status_code=404, detail="Setting not found")
    obj = SettingRead.from_orm(item)
    cache_set(cache_key, obj.dict())
    return obj

@router.put('/', response_model=List[SettingRead])
def bulk_update(payload: SettingBulkUpdate = Body(...), db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    updated = []
    for it in payload.items:
        key = it.key
        value = it.value
        setting = db.query(Setting).filter(Setting.key == key).first()
        if not setting:
            # create new with default category General and infer type
            inferred_type = 'str'
            if isinstance(value, bool):
                inferred_type = 'bool'
            elif isinstance(value, int):
                inferred_type = 'int'
            setting = Setting(key=key, value=str(value), data_type=inferred_type, category=SettingCategory.GENERAL)
            db.add(setting)
            db.commit()
            db.refresh(setting)
            updated.append(setting)
            continue
        # validate type
        expected = (setting.data_type or 'str').lower()
        try:
            if expected == 'int':
                conv = int(value)
                setting.value = str(conv)
            elif expected == 'bool':
                if isinstance(value, bool):
                    setting.value = '1' if value else '0'
                elif isinstance(value, str):
                    setting.value = '1' if value.lower() in ['1','true','yes'] else '0'
                else:
                    setting.value = '1' if bool(value) else '0'
            else:
                setting.value = str(value)
            db.add(setting)
            db.commit()
            db.refresh(setting)
            updated.append(setting)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid value for {key}: {e}")
    # invalidate caches
    try:
        if redis_client:
            for k in redis_client.keys(CACHE_PREFIX + '*'):
                redis_client.delete(k)
    except Exception:
        pass
    return [SettingRead.from_orm(u) for u in updated]

@router.post('/test-smtp')
def smtp_test(payload: Dict[str, Any] = Body(...)):
    host = payload.get('host') or settings.SMTP_HOST
    port = int(payload.get('port') or settings.SMTP_PORT)
    user = payload.get('user') or settings.SMTP_USER
    password = payload.get('password') or settings.SMTP_PASSWORD
    use_tls = bool(payload.get('tls') if 'tls' in payload else settings.SMTP_TLS)
    from_email = payload.get('from_email') or settings.EMAILS_FROM_EMAIL
    result = test_smtp(host, port, user, password, use_tls, from_email)
    if not result.get('ok'):
        raise HTTPException(status_code=400, detail=result.get('message'))
    return result
