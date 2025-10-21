from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user, role_required
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.user_service import list_users, get_user, create_user, update_user, deactivate_user
from app.models.user import User

router = APIRouter()

@router.get('/', response_model=dict)
def list_users_route(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=200), role: str = None, status: str = None, search: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items, total = list_users(db, page, per_page, role, status, search)
    return {"items": [UserRead.from_orm(u).dict() for u in items], "total": total, "page": page, "per_page": per_page}

@router.get('/{user_id}', response_model=UserRead)
def get_user_route(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return UserRead.from_orm(user)

@router.post('/', response_model=UserRead, dependencies=[Depends(role_required('Admin'))])
def create_user_route(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='User already exists')
    user = create_user(db, payload.email, payload.password, payload.name, payload.role)
    return UserRead.from_orm(user)

@router.put('/{user_id}', response_model=UserRead, dependencies=[Depends(role_required('Admin'))])
def update_user_route(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    updated = update_user(db, user, payload.dict(exclude_unset=True))
    return UserRead.from_orm(updated)

@router.delete('/{user_id}', dependencies=[Depends(role_required('Admin'))])
def delete_user_route(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    deactivated = deactivate_user(db, user)
    return {"ok": True}

@router.post('/{user_id}/change-password', dependencies=[Depends(role_required('Admin'))])
def change_password_route(user_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    new_password = payload.get('new_password')
    if not new_password:
        raise HTTPException(status_code=400, detail='new_password required')
    from app.services.user_service import change_password
    change_password(db, user, new_password)
    return {"ok": True}

@router.post('/{user_id}/assign-role', dependencies=[Depends(role_required('Admin'))])
def assign_role_route(user_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    role_name = payload.get('role')
    if not role_name:
        raise HTTPException(status_code=400, detail='role required')
    try:
        from app.services.user_service import assign_role_by_name
        assign_role_by_name(db, user, role_name)
    except ValueError:
        raise HTTPException(status_code=404, detail='Role not found')
    return {"ok": True}

@router.post('/bulk-import', response_model=List[UserRead], dependencies=[Depends(role_required('Admin'))])
def bulk_import_route(payload: List[dict], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.user_service import bulk_import_users
    created = bulk_import_users(db, payload)
    return [UserRead.from_orm(u) for u in created]
