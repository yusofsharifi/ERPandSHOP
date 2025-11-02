Reports Module (FastAPI)
=========================

Location: backend/app/api/routes/reports.py
Service: backend/app/services/reports_service.py
Tasks: backend/app/tasks/reports_tasks.py
Schemas: backend/app/schemas/reports.py

Quick start
-----------
- Ensure SQL objects from backend/sql/reports_views.sql are installed and materialized views are refreshed.
- Configure Redis (optional) by setting REDIS_URL or REDIS_HOST/REDIS_PORT in .env.
- Start Celery worker: celery -A app.celery_app.celery_app worker --loglevel=info
- Start FastAPI server and call endpoints under /api/v1/finance/reports

Configuration
-------------
- READ_REPLICA_DATABASE_URI for read-replica routing (optional)
- REDIS_URL for caching
- CACHE_TTL_SECONDS default TTL

Performance tips
----------------
- Schedule nightly refresh of mv_gl_ledger_aggregated and mv_account_summary using pg_cron or Celery periodic tasks.
- Partition journal_lines by date to accelerate drill-down queries.
- Use read replica for heavy read endpoints (reporting dashboards).

Security
--------
- Endpoints enforce role-based access via existing role_required dependency.
- Export endpoints return Celery job ids; downloads should validate job ownership in production.

