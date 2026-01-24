import pytest
from decimal import Decimal
from uuid import uuid4
from app.db.session import SessionLocal
from app.models.payroll import Employee, SalaryStructure, PayrollPeriod, Payroll
from app.services.payroll_service import _evaluate_formula, payroll_service
from app.services import gl_service as gl_svc_module
from app.services import notification_service


def test_evaluate_formula_simple():
    ctx = {'base_salary': 1000, 'overtime_hours': 10, 'rate': 50}
    val = _evaluate_formula('base_salary + overtime_hours * rate', ctx)
    assert isinstance(val, Decimal)
    assert val == Decimal('1500.00')


def test_evaluate_formula_rounding():
    ctx = {'x': 10, 'y': 3}
    val = _evaluate_formula('x / y', ctx)
    # 10/3 = 3.333..., rounded to 2 decimals -> 3.33
    assert val == Decimal('3.33')


def test_evaluate_formula_invalid():
    ctx = {'a': 1}
    with pytest.raises(ValueError):
        _evaluate_formula('import os; os.system("rm -rf /")', ctx)


@pytest.mark.integration
def test_generate_validate_pay_flow_and_gl_integration(monkeypatch):
    db = SessionLocal()
    try:
        # create employee
        emp = Employee(company_id=uuid4(), employee_code='E100', first_name='Test', last_name='User', base_salary=Decimal('1000.00'), contract_type='permanent')
        db.add(emp)
        db.commit()
        db.refresh(emp)

        # create salary structure with simple rule
        struct = SalaryStructure(name='Default', currency='IRR', rules=[{'code':'BASIC','name':'Base Salary','type':'earning','amount': 'base_salary'}], is_default=True)
        db.add(struct)
        db.commit()
        db.refresh(struct)

        # create payroll period
        period = PayrollPeriod(company_id=emp.company_id, name='TestPeriod', start_date='2025-01-01', end_date='2025-01-31')
        db.add(period)
        db.commit()
        db.refresh(period)

        # Monkeypatch GL service to return accounts and create entries
        created_journal_entries = []

        def fake_list_accounts(search=None):
            return {'total': 1, 'items': [{'id': str(uuid4())}]}

        def fake_create_journal_entry(payload, created_by=None):
            jid = str(uuid4())
            created_journal_entries.append({'id': jid, 'payload': payload})
            return {'id': jid}

        monkeypatch.setattr(gl_svc_module, 'list_accounts', fake_list_accounts)
        monkeypatch.setattr(gl_svc_module, 'create_journal_entry', fake_create_journal_entry)

        # Capture payslip emails
        sent = []
        def fake_send_payslip(db_s, employee_id, payroll_id):
            sent.append({'employee_id': str(employee_id), 'payroll_id': str(payroll_id)})
        monkeypatch.setattr(notification_service, 'send_payslip', fake_send_payslip)

        # Generate payrolls for period
        res = payroll_service.generate_for_period(db, period.id)
        assert res['payrolls_created'] == 1

        # Ensure payroll exists
        p = db.query(Payroll).filter(Payroll.employee_id == emp.id, Payroll.period_id == period.id).first()
        assert p is not None
        assert p.gross_salary >= Decimal('0.00')

        # Validate payroll -> creates journal entry
        val_res = payroll_service.validate_payroll(db, p.id)
        assert 'journal_entry_id' in val_res
        db.refresh(p)
        assert p.payment_status == 'in_progress' or str(p.payment_status) == 'in_progress'

        # Pay payroll -> creates payment journal and marks as paid
        pay_res = payroll_service.pay_payroll(db, p.id)
        assert 'journal_entry_id' in pay_res
        db.refresh(p)
        assert p.payment_status == 'paid' or str(p.payment_status) == 'paid'
        assert p.pay_date is not None

        # Ensure payslip email was (mock) sent
        assert len(sent) == 1
        assert sent[0]['employee_id'] == str(emp.id)

    finally:
        # cleanup created data
        db.query(Payroll).filter(Payroll.period_id == period.id).delete()
        db.query(PayrollPeriod).filter(PayrollPeriod.id == period.id).delete()
        db.query(SalaryStructure).filter(SalaryStructure.id == struct.id).delete()
        db.query(Employee).filter(Employee.id == emp.id).delete()
        db.commit()
        db.close()


def test_prevent_double_payroll_for_same_employee_and_period():
    db = SessionLocal()
    try:
        emp = Employee(company_id=uuid4(), employee_code='E200', first_name='D', last_name='Dup', base_salary=Decimal('500.00'), contract_type='permanent')
        db.add(emp); db.commit(); db.refresh(emp)
        period = PayrollPeriod(company_id=emp.company_id, name='P2', start_date='2025-02-01', end_date='2025-02-28')
        db.add(period); db.commit(); db.refresh(period)
        # Create first payroll via service by inserting directly
        from app.models.payroll import Payroll as PayrollModel
        p1 = PayrollModel(employee_id=emp.id, period_id=period.id, gross_salary=Decimal('500.00'), total_deductions=Decimal('0.00'), net_salary=Decimal('500.00'), payment_status='unpaid')
        db.add(p1); db.commit(); db.refresh(p1)
        # Attempt to generate for period should not create duplicate for same employee
        res = payroll_service.generate_for_period(db, period.id)
        assert res['payrolls_created'] == 0 or res['generated'] == 0
    finally:
        db.query(Payroll).filter(Payroll.period_id == period.id).delete()
        db.query(PayrollPeriod).filter(PayrollPeriod.id == period.id).delete()
        db.query(Employee).filter(Employee.id == emp.id).delete()
        db.commit(); db.close()


def test_retroactive_correction_allowed_for_different_periods():
    db = SessionLocal()
    try:
        emp = Employee(company_id=uuid4(), employee_code='E300', first_name='R', last_name='Retro', base_salary=Decimal('1000.00'), contract_type='permanent')
        db.add(emp); db.commit(); db.refresh(emp)
        # create original period and payroll
        p_old = PayrollPeriod(company_id=emp.company_id, name='Old', start_date='2025-03-01', end_date='2025-03-31')
        db.add(p_old); db.commit(); db.refresh(p_old)
        from app.models.payroll import Payroll as PayrollModel
        old_pay = PayrollModel(employee_id=emp.id, period_id=p_old.id, gross_salary=Decimal('1000.00'), total_deductions=Decimal('0.00'), net_salary=Decimal('1000.00'), payment_status='paid')
        db.add(old_pay); db.commit(); db.refresh(old_pay)
        # create correction period (different period)
        p_corr = PayrollPeriod(company_id=emp.company_id, name='Correction', start_date='2025-04-01', end_date='2025-04-30')
        db.add(p_corr); db.commit(); db.refresh(p_corr)
        # generate correction payroll for adjustment (allowed)
        res = payroll_service.generate_for_period(db, p_corr.id)
        assert res['payrolls_created'] >= 1
    finally:
        db.query(Payroll).filter(Payroll.period_id == p_old.id).delete()
        db.query(Payroll).filter(Payroll.period_id == p_corr.id).delete()
        db.query(PayrollPeriod).filter(PayrollPeriod.id.in_([p_old.id, p_corr.id])).delete()
        db.query(Employee).filter(Employee.id == emp.id).delete()
        db.commit(); db.close()
