-- sample system treasury transactions to match with bank statement
INSERT INTO treasury_transactions (id, company_id, source_type, source_id, target_type, target_id, amount, currency, exchange_rate, date, reference, posted, created_at, updated_at)
VALUES (uuid_generate_v4(),'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','other',NULL,'cash',NULL,100,'USD',1,'2021-01-01','INV-100',true,now(),now()),
(uuid_generate_v4(),'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','other',NULL,'cash',NULL,250,'USD',1,'2021-01-10','INV-101',true,now(),now());
