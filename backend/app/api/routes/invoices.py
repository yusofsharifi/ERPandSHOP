from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Optional, List
from uuid import UUID
from app.schemas import ar_ap as ap_schemas
from app.services.ar_ap_service import arap_service
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from datetime import date

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


@router.post('/', response_model=ap_schemas.InvoiceRead, status_code=201)
def create_invoice(payload: ap_schemas.InvoiceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = arap_service.create_invoice(db, payload)
    # map lines
    lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
    return ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=getattr(inv, 'invoice_no', ''), date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines)


@router.get('/', response_model=List[ap_schemas.InvoiceRead])
def list_invoices(status: Optional[str] = Query(None), date_from: Optional[date] = Query(None), date_to: Optional[date] = Query(None), customer_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    items = arap_service.list_invoices(db, status=status, partner_id=customer_id)
    results = []
    for inv in items:
        lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
        results.append(ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=getattr(inv, 'invoice_no', ''), date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines))
    return results


@router.get('/{invoice_id}', response_model=ap_schemas.InvoiceRead)
def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    inv = db.query(type(arap_service)).with_entities().first()  # dummy to keep type check
    inv = db.query(type(next(iter(db.query.__iter__()), None))).first() if False else None
    # simpler: query Invoice model
    from app.models.ar_ap import Invoice as InvoiceModel
    inv = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
    return ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=getattr(inv, 'invoice_no', ''), date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines)


@router.put('/{invoice_id}', response_model=ap_schemas.InvoiceRead)
def update_invoice(invoice_id: UUID, payload: ap_schemas.InvoiceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        inv = arap_service.update_invoice(db, invoice_id, payload)
        lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
        return ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=getattr(inv, 'invoice_no', ''), date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines)
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    except ValueError as e:
        if str(e) == 'cannot_update_non_draft':
            raise HTTPException(status_code=409, detail={"code":"cannot_update_non_draft","message":{"fa":"قابل ویرایش نیست","en":"Cannot update non-draft invoice"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.delete('/{invoice_id}')
def delete_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.ar_ap import Invoice as InvoiceModel
    inv = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    if inv.status != 'draft':
        raise HTTPException(status_code=409, detail={"code":"cannot_delete_non_draft","message":{"fa":"قابل حذف نیست","en":"Cannot delete non-draft invoice"}})
    db.delete(inv)
    db.commit()
    return {"code":"ok","deleted": True}


@router.post('/{invoice_id}/post')
def post_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = current_user
    require_role(user, 'finance_post')
    try:
        inv = arap_service.post_invoice(db, invoice_id, performed_by=user.get('id'))
        return {"code":"ok","message":{"fa":"فاکتور ثبت شد","en":"Invoice posted"}, "invoice_id": str(inv.id)}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    except ValueError as e:
        if str(e) == 'credit_limit_exceeded':
            raise HTTPException(status_code=403, detail={"code":"credit_limit_exceeded","message":{"fa":"حد اعتباری سررسیده است","en":"Credit limit exceeded"}})
        if str(e) in ['missing_gl_account','missing_gl_contra_account']:
            raise HTTPException(status_code=400, detail={"code":"missing_gl_account","message":{"fa":"حساب‌های دفتر کل پیکربندی نشده‌اند","en":"GL accounts not configured"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.post('/{invoice_id}/pay', response_model=ap_schemas.PaymentRead)
def pay_invoice(invoice_id: UUID, payload: ap_schemas.PaymentCreate = Body(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # ensure invoice id is set
    payload.invoice_id = invoice_id
    try:
        p = arap_service.record_payment(db, payload, performed_by=current_user.get('id'))
        return ap_schemas.PaymentRead(id=p.id, invoice_id=p.invoice_id, partner_id=p.partner_id, amount=p.amount, method=p.method, payment_date=p.payment_date, reference=p.reference)
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})


@router.post('/webhook/ecommerce')
def ecommerce_webhook(event: dict = Body(...)):
    # placeholder for e-commerce integration
    # accept event, validate signature later
    # queue background task for processing
    return {"received": True}
