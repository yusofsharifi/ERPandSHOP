from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Tuple
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash
from datetime import datetime


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def list_users(db: Session, page: int = 1, per_page: int = 20, role: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None) -> Tuple[List[User], int]:
    q = db.query(User)
    if role:
        q = q.join(Role).filter(Role.name == role)
    if status:
        if status.lower() == 'active':
            q = q.filter(User.is_active == True)
        elif status.lower() == 'inactive':
            q = q.filter(User.is_active == False)
    if search:
        like = f"%{search}%"
        q = q.filter((User.email.ilike(like)) | (User.name.ilike(like)))
    total = q.count()
    items = q.order_by(User.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    return items, total

def create_user(db: Session, email: str, password: str, name: Optional[str] = None, role_name: Optional[str] = None) -> User:
    hashed = get_password_hash(password)
    role = None
    if role_name:
        role = db.query(Role).filter(Role.name == role_name).first()
    user = User(email=email, hashed_password=hashed, name=name, role=role, is_active=True, created_at=datetime.utcnow())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, updates: Dict[str, Any]) -> User:
    for k, v in updates.items():
        if k == 'password':
            user.hashed_password = get_password_hash(v)
        elif k == 'role':
            role = db.query(Role).filter(Role.name == v).first()
            if role:
                user.role = role
        elif hasattr(user, k):
            setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def deactivate_user(db: Session, user: User) -> User:
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Additional helpers
def change_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def assign_role_by_name(db: Session, user: User, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError('Role not found')
    user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def bulk_import_users(db: Session, items: List[Dict[str, Any]]) -> List[User]:
    created = []
    for it in items:
        email = it.get('email')
        password = it.get('password', 'changeme123')
        name = it.get('name')
        role = it.get('role')
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            # skip existing
            continue
        u = create_user(db, email, password, name, role)
        created.append(u)
    return created
