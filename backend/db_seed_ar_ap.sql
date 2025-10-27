-- Seed data for AR/AP module
BEGIN;

-- Partners
INSERT INTO partners (id, company_id, name, partner_type, tax_id, email, phone, address, credit_limit, currency, is_active, created_at, updated_at)
VALUES
('11111111-1111-1111-1111-111111111111','00000000-0000-0000-0000-000000000001','Demo Customer','customer','TAX123','customer@example.com','+989000000001','123 Demo St',10000,'USD',true,now(),now()),
('22222222-2222-2222-2222-222222222222','00000000-0000-0000-0000-000000000001','Demo Supplier','supplier','TAX456','supplier@example.com','+989000000002','456 Supplier Ave',5000,'USD',true,now(),now());

-- Invoice for Demo Customer
INSERT INTO invoices (id, company_id, partner_id, invoice_no, series, invoice_type, date, due_date, subtotal, tax_total, total_amount, balance_amount, currency, exchange_rate, status, created_by, created_at, updated_at)
VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','00000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111','1001','S','sale','2025-08-01','2025-08-31',1000,90,1090,1090,'USD',1,'open',NULL,now(),now());

-- Invoice lines
INSERT INTO invoice_lines (id, invoice_id, line_no, product_id, description, qty, unit_price, tax_rate, line_total, created_at, updated_at)
VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',1,NULL,'Service A',1,1000,9,1090,now(),now());

COMMIT;
