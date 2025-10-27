-- Sample data seed for BizGenius reports
BEGIN;

-- companies
INSERT INTO companies (id, name) VALUES ('00000000-0000-0000-0000-000000000001','Demo Company');

-- accounts
INSERT INTO accounts (id, company_id, code, name, type, is_active, created_at, updated_at)
VALUES
('00000000-0000-0000-0000-000000000101','00000000-0000-0000-0000-000000000001','1000','Cash','asset',true,now(),now()),
('00000000-0000-0000-0000-000000000102','00000000-0000-0000-0000-000000000001','2000','Accounts Payable','liability',true,now(),now()),
('00000000-0000-0000-0000-000000000103','00000000-0000-0000-0000-000000000001','3000','Equity','equity',true,now(),now()),
('00000000-0000-0000-0000-000000000104','00000000-0000-0000-0000-000000000001','4000','Revenue','revenue',true,now(),now()),
('00000000-0000-0000-0000-000000000105','00000000-0000-0000-0000-000000000001','5000','COGS','expense',true,now(),now());

COMMIT;
