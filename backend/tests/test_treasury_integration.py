import json
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from uuid import uuid4

client = TestClient(app)


def test_transfer_endpoint():
    # create accounts via direct DB for test
    db = SessionLocal()
    try:
        comp = uuid4()
        from app.services.treasury_service import create_cash_account, create_bank_account
        cash = create_cash_account(db, {'company_id': comp, 'code': 'TCASH', 'name': 'Test Cash', 'currency': 'USD', 'balance': 1000, 'is_active': True})
        bank = create_bank_account(db, {'company_id': comp, 'bank_name': 'TBank', 'account_number': '0001', 'currency': 'USD', 'balance': 500, 'is_active': True})
    finally:
        db.close()
    # fetch accounts
    res = client.get('/api/treasury/accounts')
    assert res.status_code == 200

    # pick two accounts
    data = res.json()
    if not data:
        pytest.skip('no accounts available')
    # find created accounts
    a_from = next((x for x in data if x.get('code') == 'TCASH' or x.get('account_number') == '0001'), data[0])
    a_to = next((x for x in data if x.get('account_number') == '0001' and x['id'] != a_from['id']), data[0])

    payload = { 'from_type': 'cash', 'from_id': a_from['id'], 'to_type': 'bank', 'to_id': a_to['id'], 'amount': 100, 'currency': 'USD' }
    r = client.post('/api/treasury/transfer', json=payload, headers={'X-User-Id':'test-user'})
    assert r.status_code in (200,201)


def test_reconciliation_upload_and_apply():
    # prepare sample CSV
    csv = 'date,description,amount,currency,reference\n2021-01-01,Seed payment,100,USD,REF100\n'
    files = {'file': ('stmt.csv', io.BytesIO(csv.encode('utf-8')), 'text/csv')}
    resp = client.post('/api/treasury/reconciliation/upload', files=files, data={'bank_account_id': '22222222-2222-2222-2222-222222222222'}, headers={'X-User-Id':'test','X-Company-Id':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'})
    assert resp.status_code == 200
    body = resp.json()
    recon_id = body.get('reconciliation_id')
    assert recon_id

    # match
    r = client.post(f'/api/treasury/reconciliation/{recon_id}/match')
    assert r.status_code == 200
    # apply
    r2 = client.post(f'/api/treasury/reconciliation/{recon_id}/apply', headers={'X-User-Id':'test'})
    assert r2.status_code == 200
    jb = r2.json()
    assert 'created' in jb
