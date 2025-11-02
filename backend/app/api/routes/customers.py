from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Optional, List
from uuid import UUID
from app.schemas.customers import CustomerCreate, CustomerRead, CustomerUpdate, CustomerNoteCreate, CustomerTransactionCreate
from app.services.customer_service import customer_service
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


@router.post('/customers', response_model=CustomerRead, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    c = customer_service.create_customer(db, payload, created_by=current_user.get('id'))
    # map partner fields
    from app.models.ar_ap import Partner
    p = db.query(Partner).filter(Partner.id == c.partner_id).first()
    return CustomerRead(id=c.id, partner_id=c.partner_id, company_id=c.company_id, customer_no=c.customer_no, name=p.name, mobile=p.partner.phone if hasattr(p,'phone') else None, email=p.email, address=p.address, national_id=c.national_id, registration_no=c.registration_no, credit_limit=float(c.credit_limit or 0), status=c.status, contacts=c.contacts, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at)


@router.get('/customers', response_model=List[CustomerRead])
def list_customers(company_id: Optional[UUID] = Query(None), search: Optional[str] = Query(None), status: Optional[str] = Query(None), limit: int = Query(50), offset: int = Query(0), db: Session = Depends(get_db)):
    items = customer_service.list_customers(db, company_id=company_id, search=search, status=status, limit=limit, offset=offset)
    results = []
    from app.models.ar_ap import Partner
    for c in items:
        p = db.query(Partner).filter(Partner.id == c.partner_id).first()
        results.append(CustomerRead(id=c.id, partner_id=c.partner_id, company_id=c.company_id, customer_no=c.customer_no, name=p.name, mobile=p.partner.phone if hasattr(p,'phone') else None, email=p.email, address=p.address, national_id=c.national_id, registration_no=c.registration_no, credit_limit=float(c.credit_limit or 0), status=c.status, contacts=c.contacts, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at))
    return results


@router.get('/customers/{customer_id}', response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    c = customer_service.get_customer(db, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})
    from app.models.ar_ap import Partner
    p = db.query(Partner).filter(Partner.id == c.partner_id).first()
    return CustomerRead(id=c.id, partner_id=c.partner_id, company_id=c.company_id, customer_no=c.customer_no, name=p.name, mobile=p.partner.phone if hasattr(p,'phone') else None, email=p.email, address=p.address, national_id=c.national_id, registration_no=c.registration_no, credit_limit=float(c.credit_limit or 0), status=c.status, contacts=c.contacts, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at)


@router.put('/customers/{customer_id}', response_model=CustomerRead)
def update_customer(customer_id: UUID, payload: CustomerUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        c = customer_service.update_customer(db, customer_id, payload, performed_by=current_user.get('id'))
        from app.models.ar_ap import Partner
        p = db.query(Partner).filter(Partner.id == c.partner_id).first()
        return CustomerRead(id=c.id, partner_id=c.partner_id, company_id=c.company_id, customer_no=c.customer_no, name=p.name, mobile=p.partner.phone if hasattr(p,'phone') else None, email=p.email, address=p.address, national_id=c.national_id, registration_no=c.registration_no, credit_limit=float(c.credit_limit or 0), status=c.status, contacts=c.contacts, notes=c.notes, created_at=c.created_at, updated_at=c.updated_at)
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})


@router.delete('/customers/{customer_id}')
def delete_customer(customer_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        customer_service.delete_customer(db, customer_id, performed_by=current_user.get('id'))
        return {"code":"ok","deleted": True}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})


@router.get('/customers/{customer_id}/transactions')
def customer_transactions(customer_id: UUID, db: Session = Depends(get_db)):
    try:
        res = customer_service.list_transactions(db, customer_id)
        return res
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})


@router.post('/customers/{customer_id}/notes', status_code=201)
def add_customer_note(customer_id: UUID, payload: CustomerNoteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        n = customer_service.add_note(db, customer_id, payload.note, created_by=current_user.get('id'))
        return n
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})


@router.post('/customers/{customer_id}/transactions', status_code=201)
def add_customer_transaction(customer_id: UUID, payload: CustomerTransactionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.customers import CustomerTransaction
    c = db.query(CustomerTransaction).filter(False).first() if False else None
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail={"code":"customer_not_found","message":{"fa":"مشتری یافت نشد","en":"Customer not found"}})
    txn = CustomerTransaction(customer_id=customer_id, amount=payload.amount, transaction_type=payload.transaction_type, reference_id=payload.reference_id, date=payload.date or datetime.utcnow())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn
