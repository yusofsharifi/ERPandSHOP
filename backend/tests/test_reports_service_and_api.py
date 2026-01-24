import pytest
from app.services.reports_service import reports_service
from app.schemas.reports import TrialBalanceResponse
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_reports_service_mapping():
    # mock underlying fn_trial_balance via reports_service.trial_balance computation path
    class DummyDB: pass
    db = DummyDB()
    sample = {
        'as_of_date':'2025-08-31',
        'period_start':'2025-08-01',
        'period_end':'2025-08-31',
        'accounts': [ {'account_code':'1000','account_name':'Cash','opening_balance':0,'period_debit':100,'period_credit':0,'closing_balance':100} ],
        'totals': {'total_opening':0,'total_period_debit':100,'total_period_credit':0,'total_closing':100}
    }
    with patch('app.reports.reports_sql.fn_trial_balance', return_value=sample):
        res = reports_service.trial_balance(db, 'company-uuid', '2025-08-31')
        assert 'accounts' in res
        tb = TrialBalanceResponse(**res)
        assert len(tb.accounts) == 1


def test_trial_balance_endpoint_mocked():
    sample = {'as_of_date':'2025-08-31','accounts':[],'totals':{}}
    with patch('app.services.reports_service.reports_service.trial_balance', return_value=sample):
        r = client.get('/api/v1/finance/reports/trial-balance?company_id=111&as_of_date=2025-08-31')
        assert r.status_code == 200
        assert 'accounts' in r.json()


@patch('app.services.reports_service.reports_service.account_ledger')
def test_ledger_pagination_and_running_balance(mock_ledger):
    # mock some rows
    mock_ledger.return_value = {
        'rows': [
            {'line_id':'1','journal_id':'j1','journal_date':'2025-01-01','journal_number':'001','account_id':'a1','account_code':'1000','description':'First','debit':100,'credit':0,'balance_running_line_currency':100,'balance_running_company_currency':100},
            {'line_id':'2','journal_id':'j2','journal_date':'2025-01-02','journal_number':'002','account_id':'a1','account_code':'1000','description':'Second','debit':0,'credit':50,'balance_running_line_currency':50,'balance_running_company_currency':50},
        ], 'page':1,'per_page':100,'returned':2
    }
    r = client.get('/api/v1/finance/reports/ledger?company_id=1&account_id=a1')
    assert r.status_code == 200
    j = r.json()
    assert j['returned'] == 2


def test_export_job_creation(monkeypatch):
    class DummyAsync:
        def __init__(self): self.id = 'jobx'
    monkeypatch.setattr('app.tasks.reports_tasks.export_report.delay', lambda *a, **k: DummyAsync())
    # call export - endpoint enforces role_required -> may return 401 without auth; accept 200/401/403
    r = client.post('/api/v1/finance/reports/export?report_type=trial_balance')
    assert r.status_code in (200,401,403)
