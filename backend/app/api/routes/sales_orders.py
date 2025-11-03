from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Optional, List
from uuid import UUID
from app.schemas import sales_orders as so_schemas
from app.services.sales_order_service import sales_order_service
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request):
    user_id = request.headers.get("X-User-Id")
    roles = request.headers.get("X-User-Roles", "").split(",") if request.headers.get("X-User-Roles") else []
    return {"id": user_id, "roles": roles}


def require_role(user, role: str):
    if not user:
        raise HTTPException(status_code=401, detail={"code":"unauthorized","message":{"fa":"ناشناس","en":"Unauthorized"}})
    if role not in user.get("roles", []) and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail={"code":"forbidden","message":{"fa":"دسترسی کافی نیست","en":"Forbidden"}})


@router.post('/', response_model=so_schemas.SalesOrderRead, status_code=201)
def create_order(payload: so_schemas.SalesOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    o = sales_order_service.create_order(db, payload, created_by=current_user.get('id'))
    return o


@router.get('/', response_model=List[so_schemas.SalesOrderRead])
def list_orders(status: Optional[str] = Query(None), customer_id: Optional[UUID] = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None), db: Session = Depends(get_db)):
    df = date_from
    dt = date_to
    items = sales_order_service.list_orders(db, status=status, customer_id=customer_id, date_from=df, date_to=dt)
    return items


@router.get('/{order_id}', response_model=so_schemas.SalesOrderRead)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    o = sales_order_service.get_order(db, order_id)
    if not o:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    return o


@router.put('/{order_id}', response_model=so_schemas.SalesOrderRead)
def update_order(order_id: UUID, payload: so_schemas.SalesOrderUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        o = sales_order_service.update_order(db, order_id, payload, performed_by=current_user.get('id'))
        return o
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    except ValueError as e:
        if str(e) == 'cannot_update_non_draft':
            raise HTTPException(status_code=409, detail={"code":"cannot_update_non_draft","message":{"fa":"قابل ویرایش نیست","en":"Cannot update non-draft order"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.delete('/{order_id}')
def delete_order(order_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        sales_order_service.delete_order(db, order_id, performed_by=current_user.get('id'))
        return {"code":"ok","deleted": True}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    except ValueError:
        raise HTTPException(status_code=409, detail={"code":"cannot_delete_non_draft","message":{"fa":"قابل حذف نیست","en":"Cannot delete non-draft order"}})


@router.post('/{order_id}/confirm')
def confirm_order(order_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = current_user
    require_role(user, 'Sales')
    try:
        o = sales_order_service.confirm_order(db, order_id, performed_by=user.get('id'))
        return o
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    except ValueError as e:
        if str(e) == 'credit_limit_exceeded':
            raise HTTPException(status_code=403, detail={"code":"credit_limit_exceeded","message":{"fa":"حد اعتباری سررسیده است","en":"Credit limit exceeded"}})
        if str(e) == 'insufficient_stock':
            raise HTTPException(status_code=409, detail={"code":"insufficient_stock","message":{"fa":"موجودی کافی نیست","en":"Insufficient stock"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.post('/{order_id}/invoice')
def invoice_order(order_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = current_user
    require_role(user, 'Sales')
    try:
        res = sales_order_service.invoice_order(db, order_id, performed_by=user.get('id'))
        return res
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.post('/{order_id}/ship')
def ship_order(order_id: UUID, carrier: Optional[str] = Body(None), tracking_code: Optional[str] = Body(None), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = current_user
    require_role(user, 'Sales')
    try:
        o = sales_order_service.ship_order(db, order_id, carrier=carrier, tracking_code=tracking_code, performed_by=user.get('id'))
        return o
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"order_not_found","message":{"fa":"سفارش یافت نشد","en":"Order not found"}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})
