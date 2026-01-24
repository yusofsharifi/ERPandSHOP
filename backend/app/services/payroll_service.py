from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.models.payroll import (
    Payroll, PayrollLine, SalaryStructure, Employee, PayrollPeriod, Deduction, Bonus
)
from app.schemas import payroll as payroll_schemas
from app.services.gl_service import gl_service
from app.schemas.gl import JournalLineIn, JournalEntryCreate
from app.services import notification_service
import sqlalchemy as sa


def _sum_json_amounts(js: Optional[Dict[str, Any]]) -> Decimal:
    if not js:
        return Decimal('0.00')
    total = Decimal('0.00')
    for v in js.values():
        try:
            total += Decimal(str(v))
        except Exception:
            continue
    return total


def _evaluate_formula(formula: str, context: Dict[str, Any]) -> Decimal:
    if not formula:
        return Decimal('0.00')
    safe = formula
    for k, v in context.items():
        try:
            safe = safe.replace(k, str(v))
        except Exception:
            continue
    # very small sandbox: disallow letters after replacement
    for ch in safe:
        if ch.isalpha():
            raise ValueError('invalid_formula')
    try:
        val = Decimal(str(eval(safe, {"__builtins__": None}, {})))
    except Exception:
        raise ValueError('invalid_formula')
    return val.quantize(Decimal('0.01'))


class PayrollService:
    def list_employees(self, db: Session) -> List[Employee]:
        return db.query(Employee).order_by(Employee.first_name, Employee.last_name).all()

    def create_or_update_structure(self, db: Session, payload: payroll_schemas.SalaryStructureCreate, struct_id: Optional[UUID] = None):
        if struct_id:
            s = db.query(SalaryStructure).filter(SalaryStructure.id == struct_id).first()
            if not s:
                raise KeyError('structure_not_found')
            s.name = payload.name
            s.description = payload.description
            s.currency = payload.currency
            s.rules = payload.rules
            s.is_default = payload.is_default
        else:
            s = SalaryStructure(name=payload.name, description=payload.description, currency=payload.currency, rules=payload.rules, is_default=payload.is_default)
            db.add(s)
        db.commit()
        db.refresh(s)
        return s

    def list_periods(self, db: Session) -> List[PayrollPeriod]:
        return db.query(PayrollPeriod).order_by(PayrollPeriod.start_date.desc()).all()

    def create_period(self, db: Session, payload: payroll_schemas.PayrollPeriodCreate, created_by: Optional[UUID] = None):
        p = PayrollPeriod(company_id=payload.company_id, name=payload.name, start_date=payload.start_date, end_date=payload.end_date, created_by=created_by)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p

    def generate_for_period(self, db: Session, period_id: UUID, created_by: Optional[UUID] = None) -> Dict[str,int]:
        period = db.query(PayrollPeriod).filter(PayrollPeriod.id == period_id).first()
        if not period:
            raise KeyError('period_not_found')
        if period.status != 'draft' and str(period.status) != 'draft':
            raise ValueError('cannot_generate_non_draft')
        employees = db.query(Employee).filter(Employee.is_active == True).all()
        default_struct = db.query(SalaryStructure).filter(SalaryStructure.is_default == True).first()
        payrolls_created = 0
        lines_created = 0
        for emp in employees:
            exists = db.query(Payroll).filter(Payroll.employee_id == emp.id, Payroll.period_id == period.id).first()
            if exists:
                continue
            struct = default_struct
            rules = struct.rules if struct else []
            context = {
                'base_salary': float(emp.base_salary or 0),
            }
            gross = Decimal('0.00')
            deductions_total = Decimal('0.00')
            payroll = Payroll(employee_id=emp.id, period_id=period.id, structure_id=(struct.id if struct else None))
            db.add(payroll)
            db.flush()
            payrolls_created += 1
            if isinstance(rules, list):
                for idx, comp in enumerate(rules):
                    code = comp.get('code')
                    name = comp.get('name')
                    ctype = comp.get('type')
                    formula = comp.get('formula')
                    amount = comp.get('amount')
                    amt = Decimal('0.00')
                    if formula:
                        try:
                            amt = _evaluate_formula(formula, context)
                        except Exception:
                            amt = Decimal('0.00')
                    elif amount is not None:
                        try:
                            amt = Decimal(str(amount))
                        except Exception:
                            amt = Decimal('0.00')
                    if ctype == 'earning':
                        gross += amt
                        pl = PayrollLine(payroll_id=payroll.id, code=code or f'c{idx+1}', name=name or code or '', type='earning', amount=amt, formula=formula)
                        db.add(pl)
                        lines_created += 1
                    else:
                        deductions_total += amt
                        pl = PayrollLine(payroll_id=payroll.id, code=code or f'c{idx+1}', name=name or code or '', type='deduction', amount=amt, formula=formula)
                        db.add(pl)
                        lines_created += 1
            if gross == Decimal('0.00'):
                gross = Decimal(str(emp.base_salary or 0))
                pl = PayrollLine(payroll_id=payroll.id, code='BASIC', name='Base Salary', type='earning', amount=gross)
                db.add(pl)
                lines_created += 1
            payroll.gross_salary = gross
            payroll.total_deductions = deductions_total
            payroll.net_salary = (gross - deductions_total).quantize(Decimal('0.01'))
            payroll.payment_status = 'unpaid'
            db.commit()
        period.status = 'validated'
        db.commit()
        try:
            notification_service.send_to_role(db, 'HR', 'Payroll generated', f'Payroll for period {period.name} generated', type='info')
        except Exception:
            pass
        return {'generated': lines_created, 'payrolls_created': payrolls_created}

    def get_payroll_detail(self, db: Session, payroll_id: UUID):
        p = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if not p:
            raise KeyError('payroll_not_found')
        lines = db.query(PayrollLine).filter(PayrollLine.payroll_id == p.id).all()
        deductions = db.query(Deduction).filter(Deduction.payroll_id == p.id).all()
        bonuses = db.query(Bonus).filter(Bonus.payroll_id == p.id).all()
        return {
            'payroll': p,
            'lines': lines,
            'deductions': deductions,
            'bonuses': bonuses,
        }

    def validate_payroll(self, db: Session, payroll_id: UUID, performed_by: Optional[UUID] = None):
        p = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if not p:
            raise KeyError('payroll_not_found')
        if str(p.payment_status) != 'unpaid' and p.payment_status != 'unpaid':
            raise ValueError('already_validated_or_paid')
        expense_accs = gl_service.list_accounts(search='salary')
        if expense_accs.get('total',0) == 0:
            raise ValueError('missing_gl_expense_account')
        expense_id = expense_accs['items'][0]['id']
        payable_accs = gl_service.list_accounts(search='payable')
        if payable_accs.get('total',0) == 0:
            raise ValueError('missing_gl_payable_account')
        payable_id = payable_accs['items'][0]['id']
        total = Decimal(str(p.gross_salary))
        lines_payload = [
            JournalLineIn(line_no=1, account_id=expense_id, debit=total, credit=0),
            JournalLineIn(line_no=2, account_id=payable_id, debit=0, credit=total),
        ]
        payload = JournalEntryCreate(
            company_id=getattr(p.employee,'company_id',None),
            fiscal_year=datetime.utcnow().year,
            period=str(datetime.utcnow().month),
            date=datetime.utcnow().date(),
            description=f"Payroll for {p.employee_id} period {p.period_id}",
            lines=lines_payload,
        )
        je = gl_service.create_journal_entry(payload, created_by=performed_by)
        jid = je.get('id') if isinstance(je, dict) else getattr(je, 'id', None)
        p.journal_entry_id = jid
        p.payment_status = 'in_progress'
        db.commit()
        try:
            notification_service.send_to_role(db, 'Accounting', 'Payroll validated', f'Payroll {p.id} validated', type='info')
        except Exception:
            pass
        return {'payroll_id': p.id, 'journal_entry_id': jid}

    def pay_payroll(self, db: Session, payroll_id: UUID, performed_by: Optional[UUID] = None, pay_date: Optional[date] = None):
        p = db.query(Payroll).filter(Payroll.id == payroll_id).first()
        if not p:
            raise KeyError('payroll_not_found')
        if str(p.payment_status) == 'paid' or p.payment_status == 'paid':
            raise ValueError('already_paid')
        payable_accs = gl_service.list_accounts(search='payable')
        if payable_accs.get('total',0) == 0:
            raise ValueError('missing_gl_payable_account')
        payable_id = payable_accs['items'][0]['id']
        cash_accs = gl_service.list_accounts(search='cash')
        if cash_accs.get('total',0) == 0:
            raise ValueError('missing_gl_cash_account')
        cash_id = cash_accs['items'][0]['id']
        total = Decimal(str(p.net_salary))
        lines_payload = [
            JournalLineIn(line_no=1, account_id=payable_id, debit=total, credit=0),
            JournalLineIn(line_no=2, account_id=cash_id, debit=0, credit=total),
        ]
        payload = JournalEntryCreate(
            company_id=getattr(p.employee,'company_id',None),
            fiscal_year=datetime.utcnow().year,
            period=str(datetime.utcnow().month),
            date=pay_date or datetime.utcnow().date(),
            description=f"Payroll payment for {p.employee_id} period {p.period_id}",
            lines=lines_payload,
        )
        je = gl_service.create_journal_entry(payload, created_by=performed_by)
        jid = je.get('id') if isinstance(je, dict) else getattr(je, 'id', None)
        p.journal_entry_id = jid
        p.payment_status = 'paid'
        p.pay_date = pay_date or datetime.utcnow().date()
        db.commit()
        try:
            notification_service.send_payslip(db, p.employee_id, p.id)
        except Exception:
            pass
        return {'payroll_id': p.id, 'journal_entry_id': jid}

    def payroll_report(self, db: Session, query: payroll_schemas.PayrollReportQuery):
        q = db.query(Payroll)
        if query.company_id:
            q = q.join(Employee).filter(Employee.company_id == query.company_id)
        if query.period_id:
            q = q.filter(Payroll.period_id == query.period_id)
        if query.department_id:
            q = q.join(Employee).filter(Employee.department_id == query.department_id)
        items = q.all()
        rows: Dict[str, Dict[str, Decimal]] = {}
        total_gross = Decimal('0.00')
        total_deductions = Decimal('0.00')
        total_net = Decimal('0.00')
        for p in items:
            key = str(p.employee_id)
            rows.setdefault(key, {'gross': Decimal('0.00'), 'deductions': Decimal('0.00'), 'net': Decimal('0.00')})
            rows[key]['gross'] += Decimal(str(p.gross_salary))
            rows[key]['deductions'] += Decimal(str(p.total_deductions))
            rows[key]['net'] += Decimal(str(p.net_salary))
            total_gross += Decimal(str(p.gross_salary))
            total_deductions += Decimal(str(p.total_deductions))
            total_net += Decimal(str(p.net_salary))
        result_rows = [ { 'key': k, 'gross': v['gross'], 'deductions': v['deductions'], 'net': v['net'] } for k,v in rows.items() ]
        return { 'rows': result_rows, 'total_gross': total_gross, 'total_deductions': total_deductions, 'total_net': total_net }


payroll_service = PayrollService()
