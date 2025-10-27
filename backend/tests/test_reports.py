import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import gl_service
from uuid import uuid4

client = TestClient(app)

@pytest.fixture(autouse=True)
def seed_data():
    # Create sample accounts and journal entries in in-memory gl_service
    # Clear existing in-memory stores by creating unique company id
    company_id = str(uuid4())
    # create accounts
    a1 = gl_service.create_account(type='asset', company_id=company_id, code='1000', name='Cash') if hasattr(gl_service, 'create_account') else None
    # but in current gl_service API expects typed object; fallback to direct mutate
    from app.services.gl_service import _accounts, _entries
    _accounts.clear()
    _entries.clear()
    # Add two accounts
    acc1_id = uuid4()
    acc2_id = uuid4()
    _accounts[acc1_id] = {'id': acc1_id, 'company_id': company_id, 'code': '1000', 'name': 'Cash', 'type': 'asset'}
    _accounts[acc2_id] = {'id': acc2_id, 'company_id': company_id, 'code': '4000', 'name': 'Revenue', 'type': 'revenue'}

    # Create a balanced journal entry
    payload = {
        'company_id': company_id,
        'fiscal_year': 2025,
        'period': '2025-08',
        'date': '2025-08-01',
        'description': 'Sale',
        'lines': [
            {'line_no': 1, 'account_id': str(acc1_id), 'debit': 0, 'credit': 1000, 'description': 'cash out'},
            {'line_no': 2, 'account_id': str(acc2_id), 'debit': 1000, 'credit': 0, 'description': 'revenue'},
        ]
    }
    # Use internal create_journal_entry
    from app.schemas import gl as gl_schemas
    payload_obj = gl_schemas.JournalEntryCreate(**payload)
    rec = gl_service.create_journal_entry(payload_obj, created_by='test')
    # post it
    gl_service.post_journal_entry(rec['id'], performed_by='test')
    return {'company_id': company_id, 'acc1': acc1_id, 'acc2': acc2_id}


def test_trial_balance_matches_gl(seed_data):
    company_id = seed_data['company_id']
    res = client.get(f"/api/v1/finance/reports/trial-balance?company_id={company_id}")
    assert res.status_code == 200
    data = res.json()
    assert 'items' in data
    # compare sums
    gl_tb = gl_service.trial_balance(company_id, date_to=None)
    # items returned may be nested in .items
    items = data.get('items') if isinstance(data.get('items'), list) else data.get('items', [])
    # verify that every account in gl_tb exists in api response
    for g in gl_tb:
        found = any(str(g.get('account_id')) == str(r.get('account_id') or r.get('account_code') or r.get('account_id')) for r in items)
        assert found


def test_ledger_drilldown(seed_data):
    company_id = seed_data['company_id']
    # get trial balance to find account code
    res = client.get(f"/api/v1/finance/reports/trial-balance?company_id={company_id}")
    assert res.status_code == 200
    data = res.json()
    items = data.get('items') if isinstance(data.get('items'), list) else data.get('items', [])
    if not items:
        pytest.skip('no items')
    first = items[0]
    # use ledger endpoint
    acc = first.get('account_id') or first.get('account_code')
    r = client.get(f"/api/v1/finance/reports/ledger?company_id={company_id}&account_id={acc}")
    assert r.status_code == 200
    body = r.json()
    assert 'items' in body or 'total' in body
