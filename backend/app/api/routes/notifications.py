from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.api.deps import get_db, get_current_user, role_required
from app.schemas.notification import NotificationCreate, NotificationRead
from app.services.notification_service import get_notifications, create_notification, mark_notification_read, delete_notification, send_to_role, send_to_users
from app.services.email_service import send_email
from app.models.user import User

router = APIRouter()

@router.get('/', response_model=List[NotificationRead])
def list_notifications(page: int = 1, per_page: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = get_notifications(db, user_id=current_user.id, page=page, per_page=per_page)
    return items

@router.post('/', response_model=List[NotificationRead], dependencies=[Depends(role_required('Admin'))])
def send_notification(payload: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Payload may include: title, message, type, user_ids:[], role: 'RoleName', email_alert: bool"""
    title = payload.get('title')
    message = payload.get('message')
    ntype = payload.get('type', 'info')
    email_alert = bool(payload.get('email_alert', False))
    created = []
    # send to role
    role_name = payload.get('role')
    user_ids = payload.get('user_ids') or []
    if role_name:
        # send in background
        background_tasks.add_task(send_to_role, db, role_name, title, message, ntype, email_alert)
    if user_ids:
        background_tasks.add_task(send_to_users, db, user_ids, title, message, ntype, email_alert)
    # For immediate response, return an empty list or recent items
    return []

@router.put('/{notification_id}/read', response_model=NotificationRead)
def mark_read_route(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=404, detail='Notification not found')
    n = mark_notification_read(db, notification_id)
    return n

@router.delete('/{notification_id}')
def delete_notification_route(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail='Notification not found')
    # allow admin to delete any, users to delete their own
    from app.api.deps import role_required
    if n.user_id != current_user.id and current_user.role and current_user.role.name != 'Admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    ok = delete_notification(db, notification_id)
    if not ok:
        raise HTTPException(status_code=500, detail='Failed to delete')
    return {"ok": True}
