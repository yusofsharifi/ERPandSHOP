-- Financial Reports: materialized views, views, and functions
-- Filename: backend/sql/reports_views.sql
-- Requires: journal_entries, journal_lines, accounts, companies, fx_rates, treasury_transactions, payroll_journal_links

-- 1. Materialized view: mv_gl_ledger_aggregated
-- Monthly aggregates per account for fast trial balance / P&L summarization

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_gl_ledger_aggregated AS
SELECT
  je.company_id::uuid AS company_id,
  jl.account_id::uuid AS account_id,
  a.code AS account_code,
  a.name AS account_name,
  date_trunc('month', je.date)::date AS period_date,
  (date_trunc('month', je.date)::date) AS period_start,
  (date_trunc('month', je.date) + INTERVAL '1 month' - INTERVAL '1 day')::date AS period_end,
  SUM(jl.debit::numeric) AS total_debit,
  SUM(jl.credit::numeric) AS total_credit,
  SUM((jl.debit - jl.credit) * COALESCE(jl.exchange_rate, fr.rate, 1)) AS balance_converted
FROM journal_lines jl
JOIN journal_entries je ON je.id = jl.journal_id
LEFT JOIN accounts a ON a.id = jl.account_id
LEFT JOIN LATERAL (
  SELECT rate FROM fx_rates fr
  WHERE fr.from_currency = jl.currency
    AND fr.to_currency = (SELECT base_currency FROM companies c WHERE c.id = je.company_id)
    AND fr.date <= je.date
  ORDER BY fr.date DESC LIMIT 1
) fr ON true
WHERE je.status = 'posted'
GROUP BY je.company_id, jl.account_id, a.code, a.name, date_trunc('month', je.date)
WITH NO DATA;

-- Indexes for materialized view
CREATE INDEX IF NOT EXISTS idx_mv_gl_company_account_period ON mv_gl_ledger_aggregated (company_id, account_id, period_date);
CREATE INDEX IF NOT EXISTS idx_mv_gl_period_date ON mv_gl_ledger_aggregated (period_date);

-- 2. View: view_account_ledger
-- Detailed ledger rows with running balance per account (in line currency and converted)

CREATE OR REPLACE VIEW view_account_ledger AS
SELECT
  jl.id AS line_id,
  je.id AS journal_id,
  je.date AS journal_date,
  je.number AS journal_number,
  jl.account_id,
  a.code AS account_code,
  a.name AS account_name,
  jl.description,
  jl.debit,
  jl.credit,
  jl.currency,
  jl.exchange_rate,
  -- running balance in line currency
  SUM(jl.debit - jl.credit) OVER (PARTITION BY jl.account_id ORDER BY je.date, je.number, jl.id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance_running_line_currency,
  -- running balance converted to company base currency
  SUM((jl.debit - jl.credit) * COALESCE(jl.exchange_rate, fr.rate, 1)) OVER (PARTITION BY jl.account_id ORDER BY je.date, je.number, jl.id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance_running_company_currency
FROM journal_lines jl
JOIN journal_entries je ON je.id = jl.journal_id
LEFT JOIN accounts a ON a.id = jl.account_id
LEFT JOIN LATERAL (
  SELECT rate FROM fx_rates fr
  WHERE fr.from_currency = jl.currency
    AND fr.to_currency = (SELECT base_currency FROM companies c WHERE c.id = je.company_id)
    AND fr.date <= je.date
  ORDER BY fr.date DESC LIMIT 1
) fr ON true
WHERE je.status = 'posted';

-- 3. View: view_trial_balance
-- For a given as_of_date, compute opening, period debits/credits, closing
-- Note: we implement as parameterized function fn_trial_balance below for better performance

CREATE OR REPLACE VIEW view_trial_balance AS
SELECT
  a.code AS account_code,
  a.name AS account_name,
  SUM(mv_before.balance_converted) AS opening_balance,
  SUM(mv_period.total_debit) AS period_debit,
  SUM(mv_period.total_credit) AS period_credit,
  SUM(COALESCE(mv_before.balance_converted,0) + COALESCE(mv_period.total_debit,0) - COALESCE(mv_period.total_credit,0)) AS closing_balance
FROM accounts a
LEFT JOIN mv_gl_ledger_aggregated mv_period ON mv_period.account_id = a.id
LEFT JOIN mv_gl_ledger_aggregated mv_before ON mv_before.account_id = a.id
GROUP BY a.code, a.name;

-- 4. View: view_balance_sheet
CREATE OR REPLACE VIEW view_balance_sheet AS
SELECT
  a.type AS account_type,
  a.code AS account_code,
  a.name AS account_name,
  SUM((ml.debit - ml.credit) * COALESCE(ml.exchange_rate, fr.rate, 1)) AS amount
FROM journal_lines ml
JOIN journal_entries je ON je.id = ml.journal_id
JOIN accounts a ON a.id = ml.account_id
LEFT JOIN LATERAL (
  SELECT rate FROM fx_rates fr
  WHERE fr.from_currency = ml.currency
    AND fr.to_currency = (SELECT base_currency FROM companies c WHERE c.id = je.company_id)
    AND fr.date <= je.date
  ORDER BY fr.date DESC LIMIT 1
) fr ON true
WHERE je.status = 'posted'
GROUP BY a.type, a.code, a.name;

-- 5. View: view_pnl
CREATE OR REPLACE VIEW view_pnl AS
SELECT
  je.company_id,
  date_trunc('month', je.date)::date AS period_date,
  SUM(CASE WHEN a.type = 'revenue' THEN ml.credit - ml.debit ELSE 0 END) AS revenue,
  SUM(CASE WHEN a.type = 'expense' THEN ml.debit - ml.credit ELSE 0 END) AS expenses,
  SUM(CASE WHEN a.type = 'cogs' THEN ml.debit - ml.credit ELSE 0 END) AS cogs,
  SUM(CASE WHEN a.type = 'revenue' THEN ml.credit - ml.debit ELSE 0 END) - SUM(CASE WHEN a.type = 'expense' THEN ml.debit - ml.credit ELSE 0 END) AS net_operating
FROM journal_lines ml
JOIN journal_entries je ON je.id = ml.journal_id
JOIN accounts a ON a.id = ml.account_id
WHERE je.status = 'posted'
GROUP BY je.company_id, date_trunc('month', je.date);

-- 6. Views: Cash Flow (Direct and Indirect)
CREATE OR REPLACE VIEW view_cash_flow_direct AS
SELECT
  tt.company_id,
  date_trunc('month', tt.date)::date AS period_date,
  SUM(CASE WHEN tt.amount > 0 THEN tt.amount ELSE 0 END) AS cash_inflows,
  SUM(CASE WHEN tt.amount < 0 THEN abs(tt.amount) ELSE 0 END) AS cash_outflows
FROM treasury_transactions tt
WHERE tt.status = 'posted'
GROUP BY tt.company_id, date_trunc('month', tt.date);

CREATE OR REPLACE VIEW view_cash_flow_indirect AS
SELECT
  pnl.company_id,
  pnl.period_date,
  pnl.revenue - pnl.expenses AS operating_cash_flow
FROM view_pnl pnl;

-- 7. Materialized view: mv_account_summary (KPIs)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_account_summary AS
SELECT
  comp.id AS company_id,
  SUM(CASE WHEN a.type = 'asset' THEN (jl.debit - jl.credit) * COALESCE(jl.exchange_rate, fr.rate, 1) ELSE 0 END) AS total_assets,
  SUM(CASE WHEN a.type = 'liability' THEN (jl.credit - jl.debit) * COALESCE(jl.exchange_rate, fr.rate, 1) ELSE 0 END) AS total_liabilities,
  SUM(CASE WHEN a.type = 'equity' THEN (jl.credit - jl.debit) * COALESCE(jl.exchange_rate, fr.rate, 1) ELSE 0 END) AS total_equity
FROM journal_lines jl
JOIN journal_entries je ON je.id = jl.journal_id
JOIN accounts a ON a.id = jl.account_id
JOIN companies comp ON comp.id = je.company_id
LEFT JOIN LATERAL (
  SELECT rate FROM fx_rates fr
  WHERE fr.from_currency = jl.currency
    AND fr.to_currency = comp.base_currency
    AND fr.date <= je.date
  ORDER BY fr.date DESC LIMIT 1
) fr ON true
WHERE je.status = 'posted'
GROUP BY comp.id;

CREATE INDEX IF NOT EXISTS idx_mv_account_summary_company ON mv_account_summary (company_id);

-- 8. Functions: parameterized reports

-- fn_trial_balance: uses mv_gl_ledger_aggregated for speed. Returns JSON with accounts and totals
CREATE OR REPLACE FUNCTION fn_trial_balance(p_company_id UUID, p_as_of_date DATE)
RETURNS JSON LANGUAGE sql STABLE AS $$
WITH params AS (
  SELECT p_company_id::uuid AS company_id, p_as_of_date::date AS as_of_date
),
period AS (
  SELECT date_trunc('month', p.as_of_date)::date AS period_date, (date_trunc('month', p.as_of_date)::date) AS start_date, (date_trunc('month', p.as_of_date) + INTERVAL '1 month' - INTERVAL '1 day')::date AS end_date
  FROM params p
),
opening AS (
  SELECT account_id, SUM(balance_converted) AS opening_balance
  FROM mv_gl_ledger_aggregated m
  JOIN params p ON m.company_id = p.company_id
  WHERE m.period_date < (SELECT period_date FROM period)
  GROUP BY account_id
),
period_vals AS (
  SELECT account_id, SUM(total_debit) AS period_debit, SUM(total_credit) AS period_credit
  FROM mv_gl_ledger_aggregated m
  JOIN params p ON m.company_id = p.company_id
  WHERE m.period_date = (SELECT period_date FROM period)
  GROUP BY account_id
),
combined AS (
  SELECT a.code AS account_code, a.name AS account_name, COALESCE(o.opening_balance,0) AS opening_balance, COALESCE(pv.period_debit,0) AS period_debit, COALESCE(pv.period_credit,0) AS period_credit,
    (COALESCE(o.opening_balance,0) + COALESCE(pv.period_debit,0) - COALESCE(pv.period_credit,0)) AS closing_balance
  FROM accounts a
  LEFT JOIN opening o ON o.account_id = a.id
  LEFT JOIN period_vals pv ON pv.account_id = a.id
)
SELECT json_build_object(
  'as_of_date', (SELECT as_of_date FROM params),
  'period_start', (SELECT start_date FROM period),
  'period_end', (SELECT end_date FROM period),
  'accounts', json_agg(json_build_object('account_code', account_code, 'account_name', account_name, 'opening_balance', opening_balance, 'period_debit', period_debit, 'period_credit', period_credit, 'closing_balance', closing_balance)),
  'totals', json_build_object('total_opening', SUM(opening_balance), 'total_period_debit', SUM(period_debit), 'total_period_credit', SUM(period_credit), 'total_closing', SUM(closing_balance))
) FROM combined;
$$;

-- fn_account_ledger: paginated ledger for account
CREATE OR REPLACE FUNCTION fn_account_ledger(p_company_id UUID, p_account_id UUID, p_date_from DATE, p_date_to DATE, p_page INT DEFAULT 1, p_per_page INT DEFAULT 100)
RETURNS SETOF view_account_ledger LANGUAGE sql STABLE AS $$
  SELECT * FROM view_account_ledger v
  WHERE v.account_id = p_account_id
    AND v.journal_date BETWEEN COALESCE(p_date_from, '1970-01-01') AND COALESCE(p_date_to, now())
    AND v.journal_id IN (SELECT id FROM journal_entries WHERE company_id = p_company_id AND status = 'posted')
  ORDER BY v.journal_date, v.journal_number, v.line_id
  OFFSET (p_page-1)*p_per_page LIMIT p_per_page;
$$;

-- fn_balance_sheet
CREATE OR REPLACE FUNCTION fn_balance_sheet(p_company_id UUID, p_as_of_date DATE)
RETURNS TABLE(account_type TEXT, group_code TEXT, group_name TEXT, account_code TEXT, amount NUMERIC) LANGUAGE sql STABLE AS $$
  SELECT a.type, NULL::text as group_code, NULL::text as group_name, a.code, SUM((jl.debit - jl.credit) * COALESCE(jl.exchange_rate, fr.rate, 1))
  FROM journal_lines jl
  JOIN journal_entries je ON je.id = jl.journal_id
  JOIN accounts a ON a.id = jl.account_id
  LEFT JOIN LATERAL (
    SELECT rate FROM fx_rates fr
    WHERE fr.from_currency = jl.currency
      AND fr.to_currency = (SELECT base_currency FROM companies c WHERE c.id = je.company_id)
      AND fr.date <= COALESCE(p_as_of_date, je.date)
    ORDER BY fr.date DESC LIMIT 1
  ) fr ON true
  WHERE je.company_id = p_company_id AND je.status = 'posted' AND je.date <= p_as_of_date
  GROUP BY a.type, a.code;
$$;

-- fn_pnl
CREATE OR REPLACE FUNCTION fn_pnl(p_company_id UUID, p_date_from DATE, p_date_to DATE)
RETURNS TABLE(period_date DATE, revenue NUMERIC, expenses NUMERIC, cogs NUMERIC, net_operating NUMERIC) LANGUAGE sql STABLE AS $$
  SELECT date_trunc('month', je.date)::date AS period_date,
    SUM(CASE WHEN a.type = 'revenue' THEN jl.credit - jl.debit ELSE 0 END) AS revenue,
    SUM(CASE WHEN a.type = 'expense' THEN jl.debit - jl.credit ELSE 0 END) AS expenses,
    SUM(CASE WHEN a.type = 'cogs' THEN jl.debit - jl.credit ELSE 0 END) AS cogs,
    SUM(CASE WHEN a.type = 'revenue' THEN jl.credit - jl.debit ELSE 0 END) - SUM(CASE WHEN a.type = 'expense' THEN jl.debit - jl.credit ELSE 0 END) AS net_operating
  FROM journal_lines jl
  JOIN journal_entries je ON je.id = jl.journal_id
  JOIN accounts a ON a.id = jl.account_id
  WHERE je.company_id = p_company_id AND je.status = 'posted' AND je.date BETWEEN p_date_from AND p_date_to
  GROUP BY date_trunc('month', je.date)
  ORDER BY period_date;
$$;

-- fn_cashflow
CREATE OR REPLACE FUNCTION fn_cashflow(p_company_id UUID, p_date_from DATE, p_date_to DATE, p_method TEXT DEFAULT 'direct')
RETURNS TABLE(period_date DATE, cash_inflows NUMERIC, cash_outflows NUMERIC, operating_cash_flow NUMERIC) LANGUAGE plpgsql STABLE AS $$
BEGIN
  IF p_method = 'direct' THEN
    RETURN QUERY
    SELECT date_trunc('month', tt.date)::date AS period_date,
      SUM(CASE WHEN tt.amount > 0 THEN tt.amount ELSE 0 END) AS cash_inflows,
      SUM(CASE WHEN tt.amount < 0 THEN abs(tt.amount) ELSE 0 END) AS cash_outflows,
      SUM(CASE WHEN tt.amount > 0 THEN tt.amount ELSE 0 END) - SUM(CASE WHEN tt.amount < 0 THEN abs(tt.amount) ELSE 0 END) AS operating_cash_flow
    FROM treasury_transactions tt
    WHERE tt.company_id = p_company_id AND tt.status = 'posted' AND tt.date BETWEEN p_date_from AND p_date_to
    GROUP BY date_trunc('month', tt.date)
    ORDER BY period_date;
  ELSE
    RETURN QUERY
    SELECT p.period_date, pnl.revenue - pnl.expenses AS cash_inflows, 0::numeric AS cash_outflows, pnl.revenue - pnl.expenses AS operating_cash_flow
    FROM fn_pnl(p_company_id, p_date_from, p_date_to) pnl
    JOIN (SELECT DISTINCT date_trunc('month', date)::date AS period_date FROM journal_entries WHERE company_id = p_company_id AND date BETWEEN p_date_from AND p_date_to) p USING (period_date)
    ORDER BY p.period_date;
  END IF;
END;
$$;

-- Refresh helpers (examples):
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gl_ledger_aggregated;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_account_summary;

-- End of script
