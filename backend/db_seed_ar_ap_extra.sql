-- Extra seed data for AR/AP module
-- Creates 2 partners, 3 invoices (1 draft, 1 open, 1 partial), sample payments and checks

BEGIN;

-- Company id used for samples
-- Note: adjust company_id to match your environment if needed

INSERT INTO partners (id, company_id, name, partner_type, tax_id, email, credit_limit, currency, is_active, created_at, updated_at)
VALUES
('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','Sample Customer','customer','TAX001','cust@example.com',1000,'USD',true,now(),now()),
('00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','Sample Supplier','supplier','TAX002','sup@example.com',500,'USD',true,now(),now());

-- Draft invoice (not posted)
INSERT INTO invoices (id, company_id, partner_id, invoice_no, invoice_type, date, due_date, subtotal, tax_total, total_amount, balance_amount, currency, status, created_at, updated_at)
VALUES
('11111111-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','DRAFT-001','sale',now()::date, (now() + interval '30 days')::date, 100.00, 0.00, 100.00, 100.00, 'USD','draft', now(), now());

-- Open invoice (posted, unpaid)
INSERT INTO invoices (id, company_id, partner_id, invoice_no, invoice_type, date, due_date, subtotal, tax_total, total_amount, balance_amount, currency, status, created_at, updated_at)
VALUES
('22222222-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','OPEN-001','sale',(now()- interval '40 days')::date, (now() - interval '10 days')::date, 200.00, 0.00, 200.00, 200.00, 'USD','open', now(), now());

-- Partial invoice (posted, partially paid)
INSERT INTO invoices (id, company_id, partner_id, invoice_no, invoice_type, date, due_date, subtotal, tax_total, total_amount, balance_amount, currency, status, created_at, updated_at)
VALUES
('33333333-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','PARTIAL-001','sale',now()::date, (now() + interval '15 days')::date, 150.00, 0.00, 150.00, 50.00, 'USD','partial', now(), now());

-- Invoice lines
INSERT INTO invoice_lines (id, invoice_id, line_no, product_id, description, qty, unit_price, tax_rate, line_total, created_at, updated_at)
VALUES
('a1a1a1a1-0000-0000-0000-000000000001','11111111-0000-0000-0000-000000000001',1,NULL,'Service A',1,100.00,0,100.00,now(),now()),
('b1b1b1b1-0000-0000-0000-000000000002','22222222-0000-0000-0000-000000000002',1,NULL,'Product X',2,100.00,0,200.00,now(),now()),
('c1c1c1c1-0000-0000-0000-000000000003','33333333-0000-0000-0000-000000000003',1,NULL,'Product Y',3,50.00,0,150.00,now(),now());

-- Payments (apply a partial payment to the partial invoice)
INSERT INTO payments (id, company_id, partner_id, invoice_id, amount, method, reference, date, posted, created_at)
VALUES
('p1p1p1p1-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','33333333-0000-0000-0000-000000000003',100.00,'cash','Ref-100',now()::date,true,now());

-- Sample check
INSERT INTO checks (id, company_id, partner_id, check_no, bank_name, amount, issue_date, due_date, status, created_at)
VALUES
('k1k1k1k1-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','CHK-001','Bank A',500.00,now()::date,(now()+ interval '30 days')::date,'issued',now());

COMMIT;
