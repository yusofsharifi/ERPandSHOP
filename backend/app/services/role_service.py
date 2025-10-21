from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role

def list_roles(db: Session) -> List[Role]:
    return db.query(Role).all()

def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()

def create_role(db: Session, name: str, description: str = '', permissions: dict = None) -> Role:
    r = Role(name=name, description=description, permissions=permissions or {})
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def update_role(db: Session, role: Role, permissions: dict) -> Role:
    role.permissions = permissions
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def ensure_default_roles(db: Session):
    defaults = [
        ('Admin', 'Administrator with full access', {'*': True}),
        ('Accountant', 'Accounting department', {'invoices:view': True}),
        ('Warehouse', 'Warehouse manager', {'inventory:view': True, 'inventory:edit': True}),
        ('Sales', 'Sales team', {'orders:create': True}),
        ('Customer', 'Customer role', {'orders:create': True}),
    ]
    for name, desc, perms in defaults:
        existing = db.query(Role).filter(Role.name == name).first()
        if not existing:
            create_role(db, name, desc, perms)
