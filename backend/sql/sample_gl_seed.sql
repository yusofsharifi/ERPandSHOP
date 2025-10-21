-- Sample accounts seed for General Ledger
-- Replace COMPANY_UUID with your company UUID

BEGIN;

INSERT INTO accounts (id, company_id, code, name, type, is_active, created_at, updated_at)
VALUES
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '1', 'Assets', 'asset', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '1.1', 'Current Assets', 'asset', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '1.1.1', 'Cash', 'asset', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '2', 'Liabilities', 'liability', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '3', 'Equity', 'equity', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '4', 'Revenue', 'revenue', true, now(), now()),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', '5', 'Expenses', 'expense', true, now(), now());

COMMIT;
