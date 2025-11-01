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
Run pytest in the backend folder to execute unit tests (backend/tests).

Localization
------------
API error messages and descriptions are bilingual (fa/en) where applicable.
