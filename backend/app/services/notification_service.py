from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.role import Role
from app.models.user import User
from typing import List, Optional
from app.services.email_service import send_email
from datetime import datetime


def create_notification(db: Session, title: str, message: str, type: str = 'info', user_id: Optional[int] = None) -> Notification:
    n = Notification(title=title, message=message, type=type, user_id=user_id, created_at=datetime.utcnow())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n

def get_notifications(db: Session, user_id: Optional[int] = None, page: int = 1, per_page: int = 50) -> List[Notification]:
    q = db.query(Notification).order_by(Notification.created_at.desc())
    if user_id:
        q = q.filter(Notification.user_id == user_id)
    total = q.count()
    items = q.offset((page-1)*per_page).limit(per_page).all()
    return items

def mark_notification_read(db: Session, notification_id: int):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        return None
    n.read = True
    db.commit()
    db.refresh(n)
    return n

def delete_notification(db: Session, notification_id: int):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        return None
    db.delete(n)
    db.commit()
    return True

# Send notification to all users with a given role
def send_to_role(db: Session, role_name: str, title: str, message: str, type: str = 'info', email_alert: bool = False):
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return []
    users = db.query(User).filter(User.role_id == role.id, User.is_active == True).all()
    created = []
    for u in users:
        n = create_notification(db, title, message, type, user_id=u.id)
        created.append(n)
        if email_alert and u.email:
            send_email(u.email, title, message)
    return created

# Send notification to specific user ids
def send_to_users(db: Session, user_ids: List[int], title: str, message: str, type: str = 'info', email_alert: bool = False):
    created = []
    for uid in user_ids:
        u = db.query(User).filter(User.id == uid).first()
        if not u:
            continue
        n = create_notification(db, title, message, type, user_id=u.id)
        created.append(n)
        if email_alert and u.email:
            send_email(u.email, title, message)
    return created
