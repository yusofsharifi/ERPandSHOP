-- Sample seed data for Treasury

INSERT INTO cash_accounts (id, company_id, code, name, currency, balance, is_active, created_at, updated_at)
VALUES ('11111111-1111-1111-1111-111111111111','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','CASH-01','Main Cash','IRR',1000000000,true,now(),now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO bank_accounts (id, company_id, bank_name, account_number, iban, currency, balance, routing_code, is_active, created_at, updated_at)
VALUES
('22222222-2222-2222-2222-222222222222','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','Bank Mellat','1234567890','IR820120000000123456789012', 'IRR', 500000000, '021', true, now(), now()),
('33333333-3333-3333-3333-333333333333','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','Bank Tejarat','0987654321','IR640120000000987654321098', 'USD', 10000, '022', true, now(), now())
ON CONFLICT (id) DO NOTHING;

-- sample treasury transaction: move 1,000,000 IRR from bank to cash
INSERT INTO treasury_transactions (id, company_id, source_type, source_id, target_type, target_id, amount, currency, exchange_rate, date, reference, posted, created_at, updated_at)
VALUES ('44444444-4444-4444-4444-444444444444','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','bank','22222222-2222-2222-2222-222222222222','cash','11111111-1111-1111-1111-111111111111',1000000,'IRR',1, now(), 'seed transfer', true, now(), now())
ON CONFLICT (id) DO NOTHING;

-- another sample transaction: USD transfer from USD account to cash (converted)
INSERT INTO treasury_transactions (id, company_id, source_type, source_id, target_type, target_id, amount, currency, exchange_rate, date, reference, posted, created_at, updated_at)
VALUES ('55555555-5555-5555-5555-555555555555','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','bank','33333333-3333-3333-3333-333333333333','cash','11111111-1111-1111-1111-111111111111',5000,'USD',42000, now(), 'seed usd to cash', true, now(), now())
ON CONFLICT (id) DO NOTHING;
