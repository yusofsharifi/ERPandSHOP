import os
import json
import tempfile
from app.utils.drill_token import generate_drill_token, verify_drill_token
from fastapi.testclient import TestClient
from app.main import app
from types import SimpleNamespace
from app.celery_app import celery_app

client = TestClient(app)


def test_drill_token_utils_roundtrip():
    payload = {'company_id':'c1','account_id':'a1','date_from':'2025-01-01','date_to':'2025-01-31'}
    token = generate_drill_token(payload, expires_seconds=60)
    assert isinstance(token, str)
    data = verify_drill_token(token)
    assert data is not None
    assert data['company_id'] == 'c1'


def test_export_download_endpoint(monkeypatch, tmp_path):
    # prepare fake meta and file
    job_id = 'testjob123'
    out_dir = os.path.join('uploads','exports')
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, f"{job_id}.request.json")
    path = os.path.join(out_dir, f"export_dummy_{job_id}.csv")
    with open(meta_path, 'w') as mf:
        json.dump({'job_id': job_id, 'requested_by': 'user-1'}, mf)
    with open(path, 'w') as f:
        f.write('a,b,c\n1,2,3')

    # monkeypatch celery AsyncResult to return path
    class DummyAsync:
        def __init__(self, res):
            self._res = res
            self.status = 'SUCCESS'
        @property
        def result(self):
            return self._res
    monkeypatch.setattr(celery_app, 'AsyncResult', lambda jid: DummyAsync({'path': path}))

    # override get_current_user dependency to return a dummy user with id 'user-1'
    def fake_current_user():
        return SimpleNamespace(id='user-1', role=SimpleNamespace(name='finance_view'))
    from app.api.deps import get_current_user
    app.dependency_overrides[get_current_user] = fake_current_user

    res = client.get(f'/api/v1/finance/reports/export/download/{job_id}')
    assert res.status_code == 200
    # cleanup
    app.dependency_overrides.pop(get_current_user, None)
    try:
        os.remove(meta_path)
        os.remove(path)
    except Exception:
        pass
