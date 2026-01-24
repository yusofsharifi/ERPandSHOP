# Financial Reports - Implementation notes

This module provides SQL-optimized report endpoints with caching, read-replica support, and in-memory fallbacks for local development.

Features:
- Endpoints: /api/v1/finance/reports/trial-balance, balance-sheet, pnl, cashflow, ledger
- Uses read-replica DB if `READ_REPLICA_DATABASE_URI` is set in environment
- Caching via Redis (`REDIS_URL`) with TTL configurable `CACHE_TTL_SECONDS` (default 60s). Falls back to in-memory TTL cache when Redis not available.
- Returns both raw rows and `chart` friendly JSON (type + data)
- Ledger rows include a `ledger_link` for drill-down

Local setup (.env.example):

```
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=topworx
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost/topworx
READ_REPLICA_DATABASE_URI=

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=60

# Server
SERVER_HOST=http://localhost:8000
```

Alembic:
- Migration added: `alembic/versions/0007_create_mv_trial_balance.py` (creates materialized view `mv_trial_balance`)
- Rollback: `alembic downgrade -1` will drop the materialized view

DB seed:
- See `db_seed.sql` for inserting a demo company and accounts. Use `psql -f backend/db_seed.sql` to load sample data.

Testing:
- Unit and integration tests are available under `backend/tests/` (pytest + TestClient). Run: `pytest backend/tests -q`

Security & Operational notes:
- Sensitive operations like posting journals must run within DB transactions and be executed by authorized roles. Use row-level locks for sequence generation (SELECT ... FOR UPDATE).
- Audit logs should be written to `audit_logs` table for all create/update/post operations.
- Configure daily backups and retention policy (>=30 days) via your DB provider (pg_dump + rotation or managed backups).
- Rate limiting: add a reverse-proxy (NGINX) or middleware (e.g., slowapi) in front of the API for public endpoints.
- Timezones: store timestamps in UTC and, where required, also store company-local representations (e.g., Jalali string) at application layer.

Internationalization:
- OpenAPI schemas include tag descriptions; responses and messages should use `fastapi-babel` for bilingual strings.

If you'd like, I can:
- Add full-row-level transaction examples using SQLAlchemy + SELECT FOR UPDATE
- Integrate Redis in requirements and CI
- Add Celery tasks for scheduled report emails
