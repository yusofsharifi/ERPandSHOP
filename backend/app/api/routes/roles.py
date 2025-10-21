from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, role_required
from app.schemas.role import RoleRead
from app.services.role_service import list_roles, create_role, get_role, update_role
from app.models.role import Role

router = APIRouter()

@router.get('/', response_model=List[RoleRead])
def list_roles_route(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    roles = list_roles(db)
    return roles

@router.post('/', response_model=RoleRead, dependencies=[Depends(role_required('Admin'))])
def create_role_route(payload: RoleRead, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail='Role already exists')
    r = create_role(db, payload.name, payload.description or '', payload.permissions or {})
    return r

@router.put('/{role_id}', response_model=RoleRead, dependencies=[Depends(role_required('Admin'))])
def update_role_route(role_id: int, payload: RoleRead, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    r = get_role(db, role_id)
    if not r:
        raise HTTPException(status_code=404, detail='Role not found')
    updated = update_role(db, r, payload.permissions or {})
    return updated
