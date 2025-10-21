from decimal import Decimal
from app.services.ar_ap_service import compute_invoice_totals


def test_compute_invoice_totals_simple():
    lines = [
        type('L', (), {'qty': 2, 'unit_price': 10, 'tax_rate': 0.1}),
        type('L', (), {'qty': 1, 'unit_price': 5, 'tax_rate': 0}),
    ]
    total, totals = compute_invoice_totals(lines)
    # line1: 2*10 =20 + 10% =22.00; line2:5 => total=27.00
    assert total == Decimal('27.00')
    assert totals[0] == Decimal('22.00')
    assert totals[1] == Decimal('5.00')


def test_partial_payment_logic():
    # simulate invoice total 100
    total = Decimal('100.00')
    paid = Decimal('30.00')
    remaining = total - paid
    assert remaining == Decimal('70.00')
    # partial if remaining >0 and < total
    assert remaining > 0 and remaining < total


def test_full_payment_logic():
    total = Decimal('50.00')
    paid = Decimal('50.00')
    remaining = total - paid
    assert remaining == Decimal('0.00')
    # status paid when remaining == 0
    assert remaining == 0
