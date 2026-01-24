Treasury Module
===============

Overview
--------
This module provides treasury features: cash/bank accounts, transfers, reconciliations, bank statement parsing, and check tracking.

Installation / Migration
------------------------
- Run Alembic migrations: alembic upgrade head
- Seed sample data: psql -f backend/db_seed_treasury.sql

Design Notes
------------
- All critical balance changes use SELECT ... FOR UPDATE to ensure row-level locking.
- Transfers create treasury_transactions rows and attempt to create GL journal entries via gl_service.create_journal_entry. If GL posting fails, transaction is kept for investigation.
- Reconciliation: upload CSV creates a draft; matching heuristics run in services.tasks.

Background Jobs
---------------
- daily_reconciliation_job: reminder to review reconciliations
- low_balance_check: send alerts based on thresholds

Permissions
-----------
Roles expected: treasury_view, treasury_transfer, treasury_reconcile, treasury_admin

Testing
-------
Run pytest in the backend folder to execute unit tests (backend/tests). Included tests:

- backend/tests/test_treasury.py (basic transfer tests)
- backend/tests/test_treasury_concurrency.py (concurrent transfers simulation)
- backend/tests/test_treasury_integration.py (integration using TestClient)
- backend/tests/test_reconciliation.py (parser & matching tests)

OpenAPI / Postman
-----------------
- Postman collection: backend/postman_collection_treasury.json
- OpenAPI example: backend/openapi_treasury.json

Env & Worker
------------
You can run background jobs either with Celery (recommended for production) or FastAPI BackgroundTasks for lightweight setups.

Celery (Redis broker) example env:

- CELERY_BROKER_URL=redis://redis:6379/0
- CELERY_RESULT_BACKEND=redis://redis:6379/0

Start worker:
- celery -A backend.celery_app.celery_app worker -Q treasury -l info

Alternatively, use FastAPI BackgroundTasks for on-demand tasks. See app/tasks/treasury_tasks.py for task functions.

Bank statement formats
----------------------
CSV example headers:

- date,description,amount,currency,reference

Sample CSV is provided at backend/sample_bank_statement.csv

Migration & Seed
----------------
- Run migrations: alembic upgrade head
- Load seed: psql -f backend/db_seed_treasury.sql
- Load sample system txns: psql -f backend/db_seed_system_txns.sql

Monitoring suggestions
----------------------
Collect these metrics:
- failed_transfers (counter)
- successful_transfers (counter)
- avg_transfer_latency (histogram)
- avg_reconciliation_time (histogram)
- unmatched_lines_count (gauge)
- fx_gain_loss_total (gauge)

Operational notes
-----------------
- Atomic Balance Updates: always use SELECT ... FOR UPDATE on account rows in a DB transaction. For high concurrency, use Redis locks as a second layer.
- FX Handling: record exchange_rate on all cross-currency transactions and optionally generate FX gain/loss journal entries during posting.
- Parser Extensibility: parsers are implemented as functions in app/parsers and can be extended or registered as plugins.
- Reconciliation UX: suggestions include confidence scores; manual matching via drag & drop is supported in the frontend. Apply should generate a preview and require permission treasury_reconcile.
- Security & Audit: all critical ops write into audit_logs with payload and actor. Ensure admin panel can query audit_logs for transparency.
- Notifications: low balance, bounced checks, failed transfers should create notifications via notification_service and optionally send emails.

For further help I can:
- Improve MT940 parser to support more edge cases and bank-specific layouts
- Add Prometheus metrics exporters and Grafana dashboards
- Harden reconciliation matching with ML-based matching (future)
