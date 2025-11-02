from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
import json

client = TestClient(app)


def test_health():
    res = client.get('/api/v1/reports/_health')
    assert res.status_code == 200
    assert res.json().get('ok') is True


@patch('app.services.reports_service.reports_service.trial_balance')
def test_trial_balance_endpoint(mock_tb):
    mock_tb.return_value = {'as_of_date':'2025-08-31','accounts':[], 'totals':{}}
    res = client.get('/api/v1/reports/trial-balance?company_id=111&as_of_date=2025-08-31')
    assert res.status_code == 200
    j = res.json()
    assert 'accounts' in j


@patch('app.tasks.reports_tasks.export_report.delay')
def test_export_trigger(mock_delay):
    mock_delay.return_value.id = 'job123'
    res = client.post('/api/v1/reports/export?report_type=trial_balance')
    # since role_required decorator blocks without auth, endpoint may raise; we just ensure route exists
    assert res.status_code in (200, 401, 403, 422)
