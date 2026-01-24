# AR/AP Module - README

This document describes the Accounts Receivable / Accounts Payable (AR/AP) module API, testing, seeds, and background job setup.

## Endpoints (prefix: /api/v1/arap)
- GET /partners - List partners
- POST /partners - Create partner
- GET /invoices - List invoices
- POST /invoices - Create invoice (draft)
- PUT /invoices/{invoice_id} - Update invoice (only draft)
- POST /invoices/{invoice_id}/post - Post invoice (requires role: finance_post)
- POST /payments - Record payment (requires role: finance_post)
- GET /partners/{partner_id}/ledger - Partner ledger
- GET /invoices/{invoice_id}/pdf - Render invoice HTML (for PDF)
- GET /checks, POST /checks, GET /checks/{id}, PUT /checks/{id}, POST /checks/{id}/status
- POST /overdue-check - Run overdue detection (can be called by cron)

Refer to OpenAPI /docs provided by FastAPI for full request/response schemas.

## Business rules
- Invoice creation computes subtotal, tax_total and total_amount from invoice lines.
- Posting an invoice will:
  - Validate partner credit limit (if credit limit would be exceeded, operation returns 403 with `credit_limit_exceeded`).
  - Generate sequential invoice number using an auto-numbering mechanism (database row lock to avoid concurrency issues).
  - Change status from `draft` to `open` and set `posted_at` timestamp.
- Payments can be applied to a single invoice. Payment amounts reduce invoice.balance_amount and update invoice status (partial/paid).
- Partial payments are supported; allocations may be extended in future to allow a single payment to allocate to multiple invoices.
- Checks have independent lifecycle statuses (issued, received, deposited, cleared, bounced, returned). Changing status may trigger treasury/GL posting.
- Overdue detection scans invoices with due_date < today and status in (`open`, `partial`) and generates notifications.

## Testing
- Unit tests: `pytest` is used. Example tests are in `backend/tests/` covering compute logic and service behavior.
- Integration tests: `backend/tests/test_ar_ap_api.py` uses FastAPI TestClient to exercise create/post/payment/overdue flows.

To run tests:

1. Ensure your development database is configured (see `backend/app/core/config.py`). For CI, prefer an isolated test database.
2. Run:

```bash
pip install -r backend/requirements.txt
pytest -q
```

Note: Tests use the real database configured by `SessionLocal`. For isolated tests, set DB to a temporary PostgreSQL instance or use a docker-compose setup.

## Migrations
The alembic migration for AR/AP tables is in `backend/alembic/versions/0008_ar_ap_tables.py`.

Apply migrations:

```bash
alembic upgrade head
```

## Seed data
- `backend/db_seed_ar_ap.sql` contains initial AR/AP seed.
- `backend/db_seed_ar_ap_extra.sql` contains additional sample partners, invoices, payments, and checks for testing.

Load with psql or your DB tool:

```bash
psql $DATABASE_URL -f backend/db_seed_ar_ap_extra.sql
```

## Background jobs
- Overdue invoice detection can be run via `POST /api/v1/arap/overdue-check` or scheduled via Celery beat / cron.
- Recommended setup:
  - Use Celery with a broker (RabbitMQ or Redis).
  - Workers run `app.tasks.ar_ap_tasks.run_overdue_check` which calls notification service.

Example Celery task (conceptual):

```python
from celery import Celery
from app.db.session import SessionLocal
from app.services import ar_ap_service

celery = Celery(...)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(86400.0, run_overdue.s(), name='daily overdue check')

@celery.task
def run_overdue():
    db = SessionLocal()
    try:
        # similar logic as /overdue-check endpoint
        pass
    finally:
        db.close()
```

## Environment variables
- DATABASE_URL - PostgreSQL connection string
- BACKEND_CORS_ORIGINS - CORS allowed origins (optional)

## Security & Concurrency Recommendations
- Protect posting/payment endpoints with role-based access (already checks `finance_post`).
- Use row-level locking (`SELECT ... FOR UPDATE`) when updating invoice balances and auto-number rows.
- Consider Redis locks for high-concurrency invoice number generation.

## Extensibility
- `extra_metadata` JSONB can be added to invoices/payments for marketplace/store metadata.
- For heavy reporting, use materialized views and cache (Redis) or read replicas.

## Contacts
- Maintainers: backend team

