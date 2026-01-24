from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)
API_PREFIX = "/api/v1/customers"
HEADERS_ADMIN = {"X-User-Id": "1", "X-User-Roles": "admin"}


def test_create_and_get_customer_flow():
    payload = {
        "company_id": "00000000-0000-0000-0000-000000000001",
        "name": "Test Customer X",
        "mobile": "+989121234567",
        "email": "custx@example.com",
        "address": "Tehran",
        "national_id": "1234567890",
        "registration_no": "R-100",
        "credit_limit": 1000,
        "contacts": [{"contact_name": "Ali", "position": "Manager", "phone": "+989121111111", "email": "ali@example.com"}]
    }
    r = client.post(f"{API_PREFIX}", json=payload, headers=HEADERS_ADMIN)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Test Customer X"
    cid = body["id"]

    # get by id
    r2 = client.get(f"{API_PREFIX}/{cid}")
    assert r2.status_code == 200
    b2 = r2.json()
    assert b2["id"] == cid
    assert b2["customer_no"].startswith("CUST-")

    # list
    r3 = client.get(f"{API_PREFIX}?search=Test")
    assert r3.status_code == 200
    items = r3.json()
    assert any(i["id"] == cid for i in items)

    # add note
    r4 = client.post(f"{API_PREFIX}/{cid}/notes", json={"note": "First contact"}, headers=HEADERS_ADMIN)
    assert r4.status_code == 201
    note = r4.json()
    assert note["note"] == "First contact"

    # transactions (no invoices/payments yet)
    r5 = client.get(f"{API_PREFIX}/{cid}/transactions")
    assert r5.status_code == 200
    txs = r5.json()
    assert "balance" in txs
    assert isinstance(txs["balance"], float) or isinstance(txs["balance"], int)


def test_add_transaction_entry():
    # create minimal customer
    payload = {"company_id": "00000000-0000-0000-0000-000000000001", "name": "Txn Customer"}
    r = client.post(f"{API_PREFIX}", json=payload, headers=HEADERS_ADMIN)
    assert r.status_code == 201
    cid = r.json()["id"]

    tx = {"amount": 150.5, "transaction_type": "adjustment"}
    r2 = client.post(f"{API_PREFIX}/{cid}/transactions", json=tx, headers=HEADERS_ADMIN)
    assert r2.status_code == 201
    created = r2.json()
    assert float(created["amount"]) == 150.5
