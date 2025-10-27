import json
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, timedelta

client = TestClient(app)
API_PREFIX = "/api/v1/arap"
HEADERS_ADMIN = {"X-User-Id": "1", "X-User-Roles": "admin,finance_post"}
HEADERS_USER = {"X-User-Id": "2", "X-User-Roles": "user"}


def create_partner(name, credit_limit=None):
    payload = {"name": name, "partner_type": "customer"}
    if credit_limit is not None:
        payload["credit_limit"] = str(credit_limit)
    r = client.post(f"{API_PREFIX}/partners", json=payload, headers=HEADERS_ADMIN)
    assert r.status_code == 201
    return r.json()


def create_invoice(partner_id, lines, invoice_type="sale", due_days=30):
    payload = {
        "partner_id": partner_id,
        "invoice_type": invoice_type,
        "date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=due_days)).isoformat(),
        "lines": lines,
    }
    r = client.post(f"{API_PREFIX}/invoices", json=payload, headers=HEADERS_ADMIN)
    assert r.status_code == 201
    return r.json()


def post_invoice(invoice_id):
    r = client.post(f"{API_PREFIX}/invoices/{invoice_id}/post", headers=HEADERS_ADMIN)
    return r


def create_payment(invoice_id, amount, method="cash"):
    payload = {"invoice_id": invoice_id, "amount": str(amount), "method": method}
    r = client.post(f"{API_PREFIX}/payments", json=payload, headers=HEADERS_ADMIN)
    return r


def test_invoice_creation_and_posting_and_payment_flow():
    # Create partner
    p = create_partner("Test Customer A", credit_limit=1000)
    pid = p["id"] if isinstance(p, dict) and p.get("id") else (p[0]["id"] if isinstance(p, list) else None)
    assert pid

    # Create invoice (draft)
    inv = create_invoice(pid, [{"product_id": None, "description": "Item 1", "qty": 2, "unit_price": "10.00", "tax_rate": "0.00"}])
    invoice_id = inv["id"]

    # Post invoice
    r = post_invoice(invoice_id)
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == "ok"

    # Create partial payment
    pay = create_payment(invoice_id, "5.00")
    assert pay.status_code == 201
    pay_json = pay.json()
    assert pay_json["invoice_id"] == invoice_id

    # Get invoice and check remaining balance via list endpoint
    r = client.get(f"{API_PREFIX}/invoices?", headers=HEADERS_ADMIN)
    assert r.status_code == 200
    items = r.json()
    found = [i for i in items if i["id"] == invoice_id]
    assert found
    inv_obj = found[0]
    assert float(inv_obj["total_amount"]) >= float(inv_obj["balance_amount"]) >= 0


def test_credit_limit_enforcement_on_post():
    # Create partner with low credit limit
    p = create_partner("Low Credit", credit_limit=50)
    pid = p["id"] if isinstance(p, dict) else p[0]["id"]

    # Create invoice exceeding credit limit
    inv = create_invoice(pid, [{"product_id": None, "description": "Expensive Item", "qty": 1, "unit_price": "200.00", "tax_rate": "0.00"}])
    invoice_id = inv["id"]

    # Attempt to post invoice should fail with 403 credit_limit_exceeded
    r = post_invoice(invoice_id)
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "credit_limit_exceeded"


def test_overdue_detection_job():
    # Create partner
    p = create_partner("Overdue Partner")
    pid = p["id"] if isinstance(p, dict) else p[0]["id"]

    # Create invoice with past due date
    inv = create_invoice(pid, [{"product_id": None, "description": "Late Item", "qty": 1, "unit_price": "10.00", "tax_rate": "0.00"}], due_days=-10)
    invoice_id = inv["id"]

    # Post the invoice to make it open
    r = post_invoice(invoice_id)
    assert r.status_code == 200

    # Trigger overdue-check
    r = client.post(f"{API_PREFIX}/overdue-check", headers=HEADERS_ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert "created" in body
    assert any(str(invoice_id) in s for s in body["created"]) or str(invoice_id) in body["created"]
