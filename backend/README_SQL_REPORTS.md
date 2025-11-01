Financial Reports: Views, Materialized Views and Functions
=========================================================

Location: backend/sql/reports_views.sql

Overview
--------
This module provides optimized reporting objects for large-scale GL datasets:
- materialized views for monthly aggregates (mv_gl_ledger_aggregated)
- detailed ledger view with running balances (view_account_ledger)
- summary views for trial balance, balance sheet, P&L, cash flow
- KPI materialized view (mv_account_summary)
- parameterized functions (fn_trial_balance, fn_account_ledger, fn_balance_sheet, fn_pnl, fn_cashflow)

Design notes
------------
- Uses date_trunc('month', ...) aggregates for fast monthly summarization.
- Materialized views reduce on-the-fly aggregation for BI queries.
- view_account_ledger uses window() to compute running balances, enabling drill-down.
- FX handling: if journal_line.exchange_rate set, it's used; otherwise lateral lookup into fx_rates for latest rate <= journal_date.
- All objects assume journal_entries.status = 'posted' is the canonical posted ledger.

Indexing recommendations
------------------------
- journal_lines: CREATE INDEX idx_jl_company_account_date ON journal_lines (account_id, journal_id);
- journal_entries: CREATE INDEX idx_je_company_date_posted ON journal_entries (company_id, date, posted_at);
- fx_rates: CREATE INDEX idx_fx_from_to_date ON fx_rates (from_currency, to_currency, date DESC);
- For materialized views created here we already add indexes on (company_id, account_id, period_date) and others.

Refresh strategy
----------------
- Refresh materialized views after large posting batches. Example:
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gl_ledger_aggregated;
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_account_summary;
- Schedule via pg_cron or a background worker (Celery) to run nightly for end-of-day snapshots.
- Use CONCURRENTLY to avoid locking reads (requires unique index on materialized view for CONCURRENTLY in some PG versions).

Sample usage
------------
- Trial balance JSON for company 1111 as of 2025-08-31:
  SELECT fn_trial_balance('11111111-1111-1111-1111-111111111111'::uuid, '2025-08-31');

- Paginated ledger for account:
  SELECT * FROM fn_account_ledger('company-uuid'::uuid, 'account-uuid'::uuid, '2025-01-01', '2025-12-31', 1, 100);

Multi-currency & FX notes
------------------------
- Prefer to store exchange_rate at journal_line time when posting entries (realized FX). For historic conversion, fx_rates table is used.
- For unrealized FX gain/loss reporting, consider a specialized FX revaluation job that posts adjustments and those are included in P&L or balance sheet.

Performance & scaling
---------------------
- Use mv_gl_ledger_aggregated to pre-aggregate monthly data for millions of lines; avoid running full SUMs over journal_lines in ad-hoc queries.
- For faster drill-down, consider partitioning journal_lines by date (monthly partitions) and ensure indexes on account_id and company_id.

Future improvements
-------------------
- Create partitioned materialized views per company for multi-tenant setups.
- Add materialized views for aging schedules (AR/AP) using similar windowing techniques.
- Build incremental refresh procedures to update only impacted months after posting batches.

Contact & maintenance
---------------------
- Refresh schedules should be coordinated with accounting close processes.
- Keep fx_rates updated daily for accurate historical conversions.

