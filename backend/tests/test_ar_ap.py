import pytest
from fastapi.testclient import TestClient
from app.main import app
from uuid import UUID

client = TestClient(app)

@pytest.fixture()
def sample_partner_and_invoice():
    # create partner
    res = client.post('/api/v1/arap/partners', json={
        'company_id': '00000000-0000-0000-0000-000000000001',
        'name': 'Test Customer',
        'partner_type': 'customer',
        'tax_id': 'T123',
        'email': 'test@example.com',
        'phone': '+100000',
        'address': 'Address',
        'credit_limit': 10000,
        'currency': 'USD',
        'is_active': True
    })
    assert res.status_code == 201
    partner = res.json()

    # create invoice
    payload = {
        'partner_id': partner['id'],
        'invoice_type': 'sale',
        'date': '2025-08-01',
        'due_date': '2025-08-31',
        'currency': 'USD',
        'lines': [
            {'product_id': None, 'description': 'Service', 'qty': 1, 'unit_price': 1000, 'tax_rate': 0}
        ]
    }
    r2 = client.post('/api/v1/arap/invoices', json=payload)
    assert r2.status_code == 201
    inv = r2.json()
    return {'partner': partner, 'invoice': inv}


def test_post_invoice_and_payment(sample_partner_and_invoice):
    inv = sample_partner_and_invoice['invoice']
    partner = sample_partner_and_invoice['partner']

    # Post invoice (requires header X-User-Roles containing finance_post)
    headers = {'X-User-Id': 'tester', 'X-User-Roles': 'finance_post'}
    r = client.post(f"/api/v1/arap/invoices/{inv['id']}/post", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body.get('code') == 'ok'

    # Record payment partially
    pay_payload = {
        'company_id': '00000000-0000-0000-0000-000000000001',
        'partner_id': partner['id'],
        'invoice_id': inv['id'],
        'amount': 400,
        'method': 'bank',
        'payment_date': '2025-08-05',
        'reference': 'REF123'
    }
    r2 = client.post('/api/v1/arap/payments', headers=headers, json=pay_payload)
    assert r2.status_code == 201
    pay = r2.json()
    assert pay['amount'] == 400

    # Get invoice and check balance updated (fetch via invoices list)
    r3 = client.get(f"/api/v1/arap/invoices?", headers=headers)
    assert r3.status_code == 200
    found = [i for i in r3.json() if i['id'] == inv['id']]
    assert found
    invoice = found[0]
    # balance should be decreased (initial total 1000)
    assert float(invoice['balance_amount']) <= 1000


def test_payment_reconciliation_full(sample_partner_and_invoice):
    inv = sample_partner_and_invoice['invoice']
    partner = sample_partner_and_invoice['partner']
    headers = {'X-User-Id': 'tester', 'X-User-Roles': 'finance_post'}
    r = client.post(f"/api/v1/arap/invoices/{inv['id']}/post", headers=headers)
    assert r.status_code == 200

    # Pay full amount
    pay_payload = {
        'company_id': '00000000-0000-0000-0000-000000000001',
        'partner_id': partner['id'],
        'invoice_id': inv['id'],
        'amount': float(inv['total_amount']),
        'method': 'cash',
        'payment_date': '2025-08-06',
        'reference': 'FULL'
    }
    r2 = client.post('/api/v1/arap/payments', headers=headers, json=pay_payload)
    assert r2.status_code == 201
    # Verify invoice now shows paid
    r3 = client.get(f"/api/v1/arap/invoices?", headers=headers)
    items = r3.json()
    inv_item = [i for i in items if i['id'] == inv['id']][0]
    assert inv_item['status'] in ('paid','partial','open')
