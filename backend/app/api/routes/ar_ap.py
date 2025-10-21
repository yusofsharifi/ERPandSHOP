from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Optional, List
from uuid import UUID
from app.schemas import ar_ap as ap_schemas
from app.services.ar_ap_service import arap_service
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.services.notification_service import create_notification

router = APIRouter()

# simple dependencies

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
    if role not in user.get("roles",[]) and "admin" not in user.get("roles",[]):
        raise HTTPException(status_code=403, detail={"code":"forbidden","message":{"fa":"دسترسی کافی نیست","en":"Forbidden"}})


@router.get("/partners", response_model=List[ap_schemas.PartnerRead])
def list_partners(active: Optional[bool] = Query(None), db: Session = Depends(get_db)):
    items = arap_service.list_partners(db, active=active)
    return items


@router.post("/partners", response_model=ap_schemas.PartnerRead, status_code=201)
def create_partner(payload: ap_schemas.PartnerCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = arap_service.create_partner(db, payload)
    return p


@router.get("/invoices", response_model=List[ap_schemas.InvoiceRead])
def list_invoices(type: Optional[str] = Query(None), status: Optional[str] = Query(None), partner_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    items = arap_service.list_invoices(db, invoice_type=type, status=status, partner_id=partner_id)
    # map lines
    results = []
    for inv in items:
        lines = []
        for ln in inv.lines:
            lines.append(ap_schemas.InvoiceLineRead(id=ln.id, product_id=ln.product_id, description=ln.description, qty=ln.qty, unit_price=ln.unit_price, tax_rate=ln.tax_rate, line_total=ln.line_total))
        results.append(ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=inv.invoice_no, date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines))
    return results


@router.post("/invoices", response_model=ap_schemas.InvoiceRead, status_code=201)
def create_invoice(payload: ap_schemas.InvoiceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = arap_service.create_invoice(db, payload)
    # prepare response
    lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
    return ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=inv.invoice_no, date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines)


@router.put("/invoices/{invoice_id}", response_model=ap_schemas.InvoiceRead)
def update_invoice(invoice_id: UUID, payload: ap_schemas.InvoiceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        inv = arap_service.update_invoice(db, invoice_id, payload)
        lines = [ap_schemas.InvoiceLineRead(id=l.id, product_id=l.product_id, description=l.description, qty=l.qty, unit_price=l.unit_price, tax_rate=l.tax_rate, line_total=l.line_total) for l in inv.lines]
        return ap_schemas.InvoiceRead(id=inv.id, partner_id=inv.partner_id, invoice_no=inv.invoice_no, date=inv.date, due_date=inv.due_date, total_amount=inv.total_amount, balance_amount=inv.balance_amount, currency=inv.currency, status=inv.status, invoice_type=inv.invoice_type, lines=lines)
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    except ValueError as e:
        if str(e) == 'cannot_update_non_draft':
            raise HTTPException(status_code=409, detail={"code":"cannot_update_non_draft","message":{"fa":"قابل ویرایش نیست","en":"Cannot update non-draft invoice"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.post("/invoices/{invoice_id}/post")
def post_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # permission
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


@router.post("/payments", response_model=ap_schemas.PaymentRead, status_code=201)
def create_payment(payload: ap_schemas.PaymentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = current_user
    require_role(user, 'finance_post')
    try:
        p = arap_service.record_payment(db, payload, performed_by=user.get('id'))
        return ap_schemas.PaymentRead(id=p.id, invoice_id=p.invoice_id, partner_id=p.partner_id, amount=p.amount, method=p.method, payment_date=p.payment_date, reference=p.reference)
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})


@router.get("/partners/{partner_id}/ledger")
def partner_ledger(partner_id: UUID, db: Session = Depends(get_db)):
    # read from partner_ledger view
    res = db.execute("SELECT * FROM partner_ledger WHERE partner_id = :pid ORDER BY txn_date", {'pid': str(partner_id)})
    items = [dict(r) for r in res]
    return {"items": items}


@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: UUID, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail={"code":"invoice_not_found","message":{"fa":"فاکتور یافت نشد","en":"Invoice not found"}})
    # simple text/pdf response placeholder
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=f"Invoice {inv.invoice_no} for partner {inv.partner_id}")


@router.get("/invoices/{invoice_id}/payments")
def invoice_payments(invoice_id: UUID, db: Session = Depends(get_db)):
    pays = db.query(ap_schemas.PaymentRead.__annotations__) if False else None
    # query payments
    q = db.query(ap_schemas) if False else None
    from app.models.ar_ap import Payment as PaymentModel
    items = db.query(PaymentModel).filter(PaymentModel.invoice_id == invoice_id).order_by(PaymentModel.payment_date.desc()).all()
    result = [ap_schemas.PaymentRead(id=p.id, invoice_id=p.invoice_id, partner_id=p.partner_id, amount=p.amount, method=p.method, payment_date=p.payment_date, reference=p.reference) for p in items]
    return result


# Background overdue check endpoint (can be hooked to a cron or task runner)
@router.post('/overdue-check')
def overdue_check(db: Session = Depends(get_db)):
    from datetime import date
    from app.services import notification_service
    today = date.today()
    from app.models.ar_ap import Invoice as InvoiceModel
    overdue = db.query(InvoiceModel).filter(InvoiceModel.due_date != None, InvoiceModel.due_date < today, InvoiceModel.status.in_(['open','partial'])).all()
    created = []
    for inv in overdue:
        msg = f"Invoice {inv.invoice_no} is overdue"
        notification_service.send_to_role(db, 'Accounting', 'Overdue invoice', msg, type='warning', email_alert=False)
        created.append(inv.id)
    return {"created": [str(c) for c in created]}
