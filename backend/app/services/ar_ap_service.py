from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import date
from app.models.ar_ap import Partner, Invoice, InvoiceLine, Payment
from app.schemas import ar_ap as ap_schemas
from app.services import notification_service
from app.services.gl_service import gl_service
from app.core.config import settings
import sqlalchemy as sa
from sqlalchemy.orm import Session


def compute_line_total(line: ap_schemas.InvoiceLineIn) -> Decimal:
    qty = Decimal(line.qty)
    price = Decimal(line.unit_price)
    tax = Decimal(line.tax_rate)
    pre = qty * price
    total = (pre + (pre * tax)).quantize(Decimal('0.01'))
    return total


def compute_invoice_totals(lines: List[ap_schemas.InvoiceLineIn]) -> Tuple[Decimal, List[Decimal]]:
    totals = []
    for l in lines:
        totals.append(compute_line_total(l))
    total = sum(totals) if totals else Decimal('0.00')
    return (total.quantize(Decimal('0.01')), totals)


class ARAPService:
    @staticmethod
    def list_partners(db: Session, active: Optional[bool] = None):
        q = db.query(Partner)
        if active is not None:
            q = q.filter(Partner.is_active == active)
        return q.all()

    @staticmethod
    def create_partner(db: Session, payload: ap_schemas.PartnerCreate) -> Partner:
        p = Partner(
            name=payload.name,
            partner_type=payload.partner_type,
            tax_id=payload.tax_id,
            phone=payload.phone,
            email=payload.email,
            address=payload.address,
            credit_limit=payload.credit_limit,
            is_active=payload.is_active,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p

    @staticmethod
    def get_partner(db: Session, partner_id: UUID) -> Optional[Partner]:
        return db.query(Partner).filter(Partner.id == partner_id).first()

    @staticmethod
    def list_invoices(db: Session, invoice_type: Optional[str] = None, status: Optional[str] = None, partner_id: Optional[UUID] = None):
        q = db.query(Invoice)
        if invoice_type:
            q = q.filter(Invoice.invoice_type == invoice_type)
        if status:
            q = q.filter(Invoice.status == status)
        if partner_id:
            q = q.filter(Invoice.partner_id == partner_id)
        return q.order_by(Invoice.date.desc()).all()

    @staticmethod
    def create_invoice(db: Session, payload: ap_schemas.InvoiceCreate) -> Invoice:
        total, totals = compute_invoice_totals(payload.lines)
        inv = Invoice(
            partner_id=payload.partner_id,
            invoice_type=payload.invoice_type,
            date=payload.date,
            due_date=payload.due_date,
            currency=payload.currency or 'USD',
            total_amount=total,
            balance_amount=total,
            status='draft',
        )
        db.add(inv)
        db.flush()  # get id
        # add lines
        for idx, l in enumerate(payload.lines):
            line_total = totals[idx]
            il = InvoiceLine(
                invoice_id=inv.id,
                product_id=l.product_id,
                description=l.description,
                qty=l.qty,
                unit_price=l.unit_price,
                tax_rate=l.tax_rate,
                line_total=line_total,
            )
            db.add(il)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def update_invoice(db: Session, invoice_id: UUID, payload: ap_schemas.InvoiceUpdate) -> Invoice:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            raise KeyError('invoice_not_found')
        if inv.status != 'draft':
            raise ValueError('cannot_update_non_draft')
        if payload.date:
            inv.date = payload.date
        if payload.due_date is not None:
            inv.due_date = payload.due_date
        if payload.currency:
            inv.currency = payload.currency
        if payload.lines is not None:
            # delete existing lines and recreate
            db.query(InvoiceLine).filter(InvoiceLine.invoice_id == inv.id).delete()
            total, totals = compute_invoice_totals(payload.lines)
            for idx, l in enumerate(payload.lines):
                il = InvoiceLine(
                    invoice_id=inv.id,
                    product_id=l.product_id,
                    description=l.description,
                    qty=l.qty,
                    unit_price=l.unit_price,
                    tax_rate=l.tax_rate,
                    line_total=totals[idx],
                )
                db.add(il)
            inv.total_amount = total
            inv.balance_amount = total
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def _generate_invoice_no(db: Session, company_id, series: str = '') -> str:
        # concurrency-safe invoice number generation using gl_auto_number table (row-level lock)
        year = date.today().year
        # ensure row exists
        row = db.execute("SELECT id, last_number FROM gl_auto_number WHERE company_id = :cid AND year = :yr FOR UPDATE", {'cid': str(company_id), 'yr': year}).fetchone()
        if row is None:
            # insert initial
            db.execute("INSERT INTO gl_auto_number (id, year, company_id, last_number) VALUES (gen_random_uuid(), :yr, :cid, 1)", {'yr': year, 'cid': str(company_id)})
            last = 1
        else:
            last = int(row[1]) + 1
            db.execute("UPDATE gl_auto_number SET last_number = :ln WHERE company_id = :cid AND year = :yr", {'ln': last, 'cid': str(company_id), 'yr': year})
        # Compose invoice no
        seq = str(last).zfill(6)
        inv_no = f"{series}{year}{seq}" if series else f"{year}{seq}"
        return inv_no

    def post_invoice(db: Session, invoice_id: UUID, performed_by: Optional[int] = None, require_credit_limit: bool = True):
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).with_for_update().first()
        if not inv:
            raise KeyError('invoice_not_found')
        if inv.status != 'draft':
            raise ValueError('cannot_post_non_draft')
        # recompute totals from lines
        lines = db.query(InvoiceLine).filter(InvoiceLine.invoice_id == inv.id).all()
        calc_total = Decimal('0')
        for l in lines:
            # compute line totals if not set
            amt = Decimal(l.qty or 0) * Decimal(l.unit_price or 0)
            tax = amt * (Decimal(l.tax_rate or 0) / Decimal('100'))
            line_total = (amt + tax).quantize(Decimal('0.01'))
            calc_total += line_total
        if Decimal(inv.total_amount) != calc_total:
            raise ValueError('invoice_total_mismatch')
        # credit limit enforcement
        partner = db.query(Partner).filter(Partner.id == inv.partner_id).first()
        if require_credit_limit and partner and partner.credit_limit is not None and partner.credit_limit > 0:
            # sum outstanding balances excluding this draft
            outstanding = db.query(Invoice).filter(Invoice.partner_id == partner.id, Invoice.status.in_(['open','partial'])).with_entities(sa.func.coalesce(sa.func.sum(Invoice.balance_amount),0)).scalar() or 0
            from decimal import Decimal as D
            outstanding = D(outstanding)
            if outstanding + D(inv.total_amount) > D(partner.credit_limit):
                raise ValueError('credit_limit_exceeded')
        # generate invoice_no safely
        try:
            inv_no = ARAPService._generate_invoice_no(db, inv.company_id, series=inv.series or '')
        except Exception:
            raise ValueError('invoice_number_generation_failed')
        inv.invoice_no = inv_no
        # create journal entry via gl_service: find AR/AP account
        acc_search = 'receivable' if inv.invoice_type == 'sale' else 'payable'
        accounts = gl_service.list_accounts(search=acc_search)
        if accounts.get('total',0) == 0:
            raise ValueError('missing_gl_account')
        account_id = accounts['items'][0]['id']
        # build journal lines: debit AR (account_id) total_amount, credit revenue placeholder
        from app.schemas.gl import JournalLineIn, JournalEntryCreate
        total_amt = Decimal(inv.total_amount)
        contra_search = 'revenue' if inv.invoice_type == 'sale' else 'expense'
        contra_accounts = gl_service.list_accounts(search=contra_search)
        if contra_accounts.get('total',0) == 0:
            raise ValueError('missing_gl_contra_account')
        contra_id = contra_accounts['items'][0]['id']
        lines_payload = [
            JournalLineIn(line_no=1, account_id=account_id, debit=total_amt, credit=0),
            JournalLineIn(line_no=2, account_id=contra_id, debit=0, credit=total_amt),
        ]
        payload = JournalEntryCreate(
            company_id=inv.company_id,
            fiscal_year=date.today().year,
            period=str(date.today().month),
            date=inv.date,
            description=f"Invoice {inv.invoice_no} posted",
            lines=lines_payload,
        )
        je = gl_service.create_journal_entry(payload, created_by=performed_by)
        # mark invoice as open
        inv.status = 'open'
        inv.posted_at = datetime.utcnow()
        db.add(inv)
        db.commit()
        db.refresh(inv)
        # audit
        try:
            from app.services.gl_service import gl_service as _gl
            _gl._audit('invoice', str(inv.id), 'post', {'invoice_no': inv.invoice_no, 'total_amount': str(inv.total_amount)}, performed_by=performed_by)
        except Exception:
            pass
        notification_service.send_to_role(db, 'Accounting', 'Invoice posted', f'Invoice {inv.invoice_no} posted', type='info')
        return inv

    @staticmethod
    def record_payment(db: Session, payload: ap_schemas.PaymentCreate, performed_by: Optional[int] = None):
        # record payment and adjust invoice balance atomically
        from decimal import Decimal
        p = Payment(
            invoice_id=payload.invoice_id,
            partner_id=payload.partner_id,
            amount=payload.amount,
            method=payload.method,
            payment_date=payload.payment_date,
            reference=payload.reference,
        )
        db.add(p)
        if payload.invoice_id:
            inv = db.query(Invoice).filter(Invoice.id == payload.invoice_id).with_for_update().first()
            if not inv:
                raise KeyError('invoice_not_found')
            new_balance = Decimal(inv.balance_amount) - Decimal(payload.amount)
            if new_balance <= 0:
                inv.balance_amount = Decimal('0.00')
                inv.status = 'paid'
            else:
                inv.balance_amount = new_balance
                if Decimal(inv.total_amount) > new_balance and new_balance > 0:
                    inv.status = 'partial'
            db.add(inv)
        db.commit()
        db.refresh(p)
        # create journal entry for payment via gl_service
        # find cash/bank account based on method
        method = payload.method
        account_search = 'cash' if method == 'cash' else ('bank' if method == 'bank' else 'cash')
        accs = gl_service.list_accounts(search=account_search)
        if accs.get('total',0) == 0:
            # no posting but return payment
            return p
        acc_id = accs['items'][0]['id']
        # counterpart: AR/AP account
        arap_search = 'receivable' if payload.invoice_id else 'receivable'
        arap_accs = gl_service.list_accounts(search=arap_search)
        if arap_accs.get('total',0) == 0:
            return p
        arap_id = arap_accs['items'][0]['id']
        from app.schemas.gl import JournalLineIn, JournalEntryCreate
        amt = Decimal(payload.amount)
        # if payment for sale invoice: debit cash/bank, credit receivable
        lines_payload = [
            JournalLineIn(line_no=1, account_id=acc_id, debit=amt, credit=0),
            JournalLineIn(line_no=2, account_id=arap_id, debit=0, credit=amt),
        ]
        try:
            payload_je = JournalEntryCreate(
                company_id=uuid4(),
                fiscal_year=date.today().year,
                period=str(date.today().month),
                date=payload.payment_date,
                description=f"Payment {p.id}",
                lines=lines_payload,
            )
            gl_service.create_journal_entry(payload_je, created_by=performed_by)
        except Exception:
            # swallow to avoid failing payment recording
            pass
        return p


# Export a singleton
arap_service = ARAPService()
