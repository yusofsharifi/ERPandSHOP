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
        db.execute("INSERT INTO cash_accounts (id, company_id, code, name, currency, balance, is_active, created_at, updated_at) VALUES (uuid_generate_v4(), %s, 'TCASH', 'Test Cash', 'USD', 1000, true, now(), now())", (str(comp),))
        db.execute("INSERT INTO bank_accounts (id, company_id, bank_name, account_number, currency, balance, is_active, created_at, updated_at) VALUES (uuid_generate_v4(), %s, 'TBank','0001','USD',500,true,now(),now())", (str(comp),))
        db.commit()
    finally:
        db.close()
    # fetch accounts
    res = client.get('/api/treasury/accounts')
    assert res.status_code == 200

    # pick two accounts
    data = res.json()
    if not data:
        pytest.skip('no accounts available')
    a_from = data[0]
    a_to = data[1] if len(data)>1 else data[0]

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
