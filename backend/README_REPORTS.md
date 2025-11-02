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

Usage examples
--------------
- Trial balance (curl):
  curl "http://localhost:8000/api/v1/finance/reports/trial-balance?company_id=<company_uuid>&as_of_date=2025-08-31"

Cache invalidation & refresh
----------------------------
- Materialized views should be refreshed after posting batches. Recommended strategies:
  - Trigger REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gl_ledger_aggregated after nightly posting job.
  - In high-volume environments use incremental refresh: track changed months and refresh only impacted months.
  - After refresh, invalidate report cache keys (implement a cache invalidation hook in the posting pipeline).

Read-replica guidance
----------------------
- Configure READ_REPLICA_DATABASE_URI in .env; the application will use read-replica for heavy read endpoints when available.
- Ensure replication lag is acceptable for reporting windows; for same-day reports prefer primary or implement lag-aware routing.

Export flow & retention
-----------------------
- /export enqueues a Celery job and returns job_id. Check /export/status/{job_id} for status.
- Exported files are saved under uploads/exports. Implement retention policy (e.g., delete files older than 7 days) via scheduled job.

Prometheus & monitoring
-----------------------
- Metrics exposed on /metrics (Prometheus format). Suggested metrics:
  - average_report_latency_seconds (Histogram)
  - report_cache_hit_total (Counter)
  - export_job_duration_seconds (Histogram)
  - rows_returned (Histogram)

Postman / OpenAPI
-----------------
- Postman collection: backend/postman_reports_collection.json

Testing
-------
- Unit tests that depend on SQL functions will be skipped if functions are not installed. Ensure backend/sql/reports_views.sql is applied.

Contact
-------
- For help configuring materialized view refresh schedules and read-replica setup, coordinate with DBAs or ops team.

