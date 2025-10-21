from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.payroll import PayrollRun, PayrollLine, SalaryStructure, Employee, PayrollStatusEnum
from app.schemas import payroll as payroll_schemas
from app.services.gl_service import gl_service
from app.schemas.gl import JournalLineIn, JournalEntryCreate
from app.services import notification_service
import sqlalchemy as sa


def sum_json_amounts(js: Optional[Dict[str, Any]]) -> Decimal:
    if not js:
        return Decimal('0.00')
    total = Decimal('0.00')
    # expect js like {"housing": 100, "transport": 50}
    for v in js.values():
        try:
            total += Decimal(str(v))
        except Exception:
            continue
    return total


def compute_employee_pay(base_salary: Decimal, allowances: Optional[Dict[str, Any]], deductions: Optional[Dict[str, Any]], taxable: bool) -> Dict[str, Decimal]:
    a = sum_json_amounts(allowances)
    d = sum_json_amounts(deductions)
    gross = (Decimal(base_salary) + a).quantize(Decimal('0.01'))
    taxes = Decimal('0.00')
    if taxable:
        # simple flat tax 10% for demo
        taxes = (gross * Decimal('0.10')).quantize(Decimal('0.01'))
    net = (gross - taxes - d).quantize(Decimal('0.01'))
    return { 'gross': gross, 'taxes': taxes, 'deductions': d, 'net': net }


class PayrollService:
    @staticmethod
    def create_run(db: Session, period_start, period_end, employee_ids: Optional[List[UUID]] = None, created_by: Optional[UUID] = None):
        pr = PayrollRun(period_start=period_start, period_end=period_end, status=PayrollStatusEnum.draft)
        db.add(pr)
        db.commit()
        db.refresh(pr)
        # if employee_ids provided, store lines later by compute
        return pr

    @staticmethod
    def compute_run(db: Session, payroll_id: UUID, employee_ids: Optional[List[UUID]] = None, performed_by: Optional[UUID] = None) -> Dict[str, Any]:
        pr = db.query(PayrollRun).filter(PayrollRun.id == payroll_id).first()
        if not pr:
            raise KeyError('payroll_run_not_found')
        if pr.status != PayrollStatusEnum.draft:
            raise ValueError('cannot_compute_non_draft')
        # select employees
        q = db.query(Employee).filter(Employee.is_active == True)
        if employee_ids:
            q = q.filter(Employee.id.in_(employee_ids))
        employees = q.all()
        # pick default salary structure if present
        default_struct = db.query(SalaryStructure).first()
        lines_created = 0
        for emp in employees:
            # prevent duplicates via unique constraint; check existing payroll_lines
            exists = db.query(PayrollLine).filter(PayrollLine.employee_id == emp.id, PayrollLine.period_start == pr.period_start, PayrollLine.period_end == pr.period_end).first()
            if exists:
                continue
            # use default structure
            if default_struct:
                base = Decimal(default_struct.base_salary)
                allowances = default_struct.allowances
                deductions = default_struct.deductions
                taxable = default_struct.taxable
            else:
                base = Decimal('0.00')
                allowances = {}
                deductions = {}
                taxable = False
            computed = compute_employee_pay(base, allowances, deductions, taxable)
            pl = PayrollLine(
                payroll_id=pr.id,
                employee_id=emp.id,
                period_start=pr.period_start,
                period_end=pr.period_end,
                gross=computed['gross'],
                taxes=computed['taxes'],
                deductions=computed['deductions'],
                net=computed['net'],
                components={
                    'base_salary': str(base),
                    'allowances': allowances or {},
                    'deductions': deductions or {},
                    'taxable': taxable,
                }
            )
            db.add(pl)
            lines_created += 1
        pr.generated_at = datetime.utcnow()
        pr.status = PayrollStatusEnum.computed
        db.commit()
        db.refresh(pr)
        # notify accounting
        try:
            notification_service.send_to_role(db, 'Accounting', 'Payroll computed', f'Payroll {pr.id} computed', type='info')
        except Exception:
            pass
        return { 'payroll_id': pr.id, 'lines_generated': lines_created }

    @staticmethod
    def list_runs(db: Session):
        return db.query(PayrollRun).order_by(PayrollRun.created_at.desc()).all()

    @staticmethod
    def list_lines(db: Session, payroll_id: UUID):
        return db.query(PayrollLine).filter(PayrollLine.payroll_id == payroll_id).all()

    @staticmethod
    def post_run(db: Session, payroll_id: UUID, performed_by: Optional[UUID] = None):
        pr = db.query(PayrollRun).filter(PayrollRun.id == payroll_id).first()
        if not pr:
            raise KeyError('payroll_run_not_found')
        if pr.status != PayrollStatusEnum.computed:
            raise ValueError('cannot_post_non_computed')
        lines = db.query(PayrollLine).filter(PayrollLine.payroll_id == pr.id).all()
        if not lines:
            raise ValueError('no_payroll_lines')
        # find payroll expense account and payable/cash accounts
        expense_accs = gl_service.list_accounts(search='salary')
        if expense_accs.get('total',0) == 0:
            raise ValueError('missing_gl_expense_account')
        expense_id = expense_accs['items'][0]['id']
        payable_accs = gl_service.list_accounts(search='payable')
        if payable_accs.get('total',0) == 0:
            raise ValueError('missing_gl_payable_account')
        payable_id = payable_accs['items'][0]['id']
        # sum totals
        total_gross = sum([Decimal(str(l.gross)) for l in lines])
        total_taxes = sum([Decimal(str(l.taxes)) for l in lines])
        total_deductions = sum([Decimal(str(l.deductions)) for l in lines])
        total_net = sum([Decimal(str(l.net)) for l in lines])
        # create journal entry: debit expense total_gross, credit payable total_gross (or split taxes/deductions)
        lines_payload = [
            JournalLineIn(line_no=1, account_id=expense_id, debit=total_gross, credit=0),
            JournalLineIn(line_no=2, account_id=payable_id, debit=0, credit=total_gross),
        ]
        payload = JournalEntryCreate(
            company_id=uuid4(),
            fiscal_year=datetime.utcnow().year,
            period=str(datetime.utcnow().month),
            date=pr.generated_at.date() if pr.generated_at else datetime.utcnow().date(),
            description=f"Payroll run {pr.id}",
            lines=lines_payload,
        )
        je = gl_service.create_journal_entry(payload, created_by=performed_by)
        # link journal
        from app.models.payroll import PayrollJournalLink
        link = PayrollJournalLink(payroll_run_id=pr.id, journal_entry_id=je.get('id')) if isinstance(je, dict) else PayrollJournalLink(payroll_run_id=pr.id, journal_entry_id=je.get('id'))
        # In-memory gl_service returns dict; real gl_service returns rec
        try:
            # if je is dict with id key
            jid = je.get('id') if isinstance(je, dict) else getattr(je, 'id', None)
            link = PayrollJournalLink(payroll_run_id=pr.id, journal_entry_id=jid)
            db.add(link)
        except Exception:
            pass
        pr.status = PayrollStatusEnum.posted
        db.commit()
        db.refresh(pr)
        notification_service.send_to_role(db, 'Accounting', 'Payroll posted', f'Payroll {pr.id} posted', type='info')
        return { 'payroll_id': pr.id, 'journal_entry_id': jid }


payroll_service = PayrollService()
