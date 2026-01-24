from decimal import Decimal
from app.services.payroll_service import compute_employee_pay


def test_compute_employee_pay_taxable():
    base = Decimal('1000')
    allowances = {'housing': 100, 'transport': 50}
    deductions = {'loan': 30}
    res = compute_employee_pay(base, allowances, deductions, True)
    # gross = 1000 + 150 = 1150
    assert res['gross'] == Decimal('1150.00')
    # taxes = 10% of gross = 115
    assert res['taxes'] == Decimal('115.00')
    # deductions sum = 30
    assert res['deductions'] == Decimal('30.00')
    # net = 1150 - 115 - 30 = 1005
    assert res['net'] == Decimal('1005.00')


def test_compute_employee_pay_non_taxable():
    base = Decimal('800')
    allowances = {'bonus': 200}
    deductions = {'advance': 50}
    res = compute_employee_pay(base, allowances, deductions, False)
    assert res['gross'] == Decimal('1000.00')
    assert res['taxes'] == Decimal('0.00')
    assert res['deductions'] == Decimal('50.00')
    assert res['net'] == Decimal('950.00')
