from sqlalchemy.orm import Session
from app.models.ar_ap import Partner
from app.models.customers import Customer, CustomerContact, CustomerNote, CustomerTransaction
from app.models.gl_models import AuditLog
from typing import List, Optional
from uuid import uuid4
from datetime import datetime


class CustomerService:
    @staticmethod
    def _generate_customer_no(db: Session, company_id) -> str:
        # simple sequential customer numbering per company: CUST-000001
        q = db.query(Customer).filter(Customer.company_id == company_id).order_by(Customer.created_at.desc()).first()
        if not q:
            seq = 1
        else:
            # try to parse last number
            try:
                last = db.query(Customer).filter(Customer.company_id == company_id).order_by(Customer.created_at.desc()).first()
                no = last.customer_no
                seq = int(no.split('-')[-1]) + 1
            except Exception:
                seq = 1
        return f"CUST-{seq:06d}"

    @staticmethod
    def create_customer(db: Session, payload, created_by=None):
        # create partner record first
        p = Partner(
            company_id=payload.company_id,
            name=payload.name,
            partner_type='customer',
            email=payload.email,
            phone=payload.mobile,
            address=payload.address,
            credit_limit=payload.credit_limit or 0,
            is_active=True,
        )
        db.add(p)
        db.flush()
        # create customer meta
        cust_no = CustomerService._generate_customer_no(db, payload.company_id)
        c = Customer(
            partner_id=p.id,
            company_id=payload.company_id,
            customer_no=cust_no,
            national_id=payload.national_id,
            registration_no=payload.registration_no,
            credit_limit=payload.credit_limit or 0,
            status='active',
        )
        db.add(c)
        # contacts
        for cnt in payload.contacts or []:
            cc = CustomerContact(customer=c, contact_name=cnt.contact_name, position=cnt.position, phone=cnt.phone, email=cnt.email)
            db.add(cc)
        # audit
        al = AuditLog(entity_type='customer', entity_id=c.id, action='create', payload={'customer_no': c.customer_no, 'name': p.name}, user_id=created_by)
        db.add(al)
        db.commit()
        db.refresh(c)
        return c

    @staticmethod
    def get_customer(db: Session, customer_id):
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def update_customer(db: Session, customer_id, payload, performed_by=None):
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            raise KeyError('customer_not_found')
        # update partner
        p = db.query(Partner).filter(Partner.id == c.partner_id).first()
        if payload.name is not None:
            p.name = payload.name
        if payload.email is not None:
            p.email = payload.email
        if payload.mobile is not None:
            p.phone = payload.mobile
        if payload.address is not None:
            p.address = payload.address
        if payload.credit_limit is not None:
            c.credit_limit = payload.credit_limit
            p.credit_limit = payload.credit_limit
        if payload.national_id is not None:
            c.national_id = payload.national_id
        if payload.registration_no is not None:
            c.registration_no = payload.registration_no
        if payload.status is not None:
            c.status = payload.status
            p.is_active = (payload.status == 'active')
        db.add(p)
        db.add(c)
        # audit
        al = AuditLog(entity_type='customer', entity_id=c.id, action='update', payload=payload.dict(exclude_none=True), user_id=performed_by)
        db.add(al)
        db.commit()
        db.refresh(c)
        return c

    @staticmethod
    def delete_customer(db: Session, customer_id, performed_by=None):
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            raise KeyError('customer_not_found')
        # soft delete: set status inactive
        c.status = 'deleted'
        p = db.query(Partner).filter(Partner.id == c.partner_id).first()
        if p:
            p.is_active = False
        al = AuditLog(entity_type='customer', entity_id=c.id, action='delete', payload={'deleted': True}, user_id=performed_by)
        db.add(al)
        db.add(c)
        db.add(p)
        db.commit()
        return True

    @staticmethod
    def list_customers(db: Session, company_id=None, search: Optional[str]=None, status: Optional[str]=None, limit: int=50, offset: int=0) -> List[Customer]:
        q = db.query(Customer).join(Partner, Customer.partner_id == Partner.id)
        if company_id:
            q = q.filter(Customer.company_id == company_id)
        if status:
            q = q.filter(Customer.status == status)
        if search:
            like = f"%{search}%"
            q = q.filter((Partner.name.ilike(like)) | (Partner.phone.ilike(like)) | (Partner.email.ilike(like)))
        return q.order_by(Customer.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def add_note(db: Session, customer_id, note_text, created_by=None):
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            raise KeyError('customer_not_found')
        n = CustomerNote(customer_id=c.id, note=note_text, created_by=created_by)
        db.add(n)
        al = AuditLog(entity_type='customer_note', entity_id=n.id, action='create', payload={'note': note_text}, user_id=created_by)
        db.add(al)
        db.commit()
        db.refresh(n)
        return n

    @staticmethod
    def list_transactions(db: Session, customer_id):
        # aggregate invoices/payments + custom transactions
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if not c:
            raise KeyError('customer_not_found')
        # from invoices and payments
        inv_sum = db.execute("SELECT COALESCE(SUM(total_amount),0) as total_invoices FROM invoices WHERE partner_id = :pid", {'pid': str(c.partner_id)}).scalar() or 0
        pay_sum = db.execute("SELECT COALESCE(SUM(amount),0) as total_payments FROM payments WHERE partner_id = :pid", {'pid': str(c.partner_id)}).scalar() or 0
        # custom transactions
        custom = db.query(CustomerTransaction).filter(CustomerTransaction.customer_id == customer_id).all()
        balance = float(inv_sum) - float(pay_sum)
        txs = [{ 'type': 'invoice_total', 'amount': float(inv_sum) }, { 'type': 'payment_total', 'amount': float(pay_sum) }]
        for t in custom:
            txs.append({'id': t.id, 'type': t.transaction_type, 'amount': float(t.amount), 'date': t.date})
        return { 'balance': balance, 'transactions': txs }


customer_service = CustomerService()
