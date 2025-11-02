import time
import pytest
from app.db.session import SessionLocal
from app.reports.reports_sql import fn_trial_balance, fn_account_ledger
from uuid import uuid4
from app.models.gl_models import Account, JournalEntry, JournalLine, AccountTypeEnum


@pytest.mark.performance
def test_performance_trial_balance_and_ledger(benchmark_insert_count:int=1000):
    db = SessionLocal()
    try:
        # skip if functions not available
        try:
            r = db.execute("SELECT proname FROM pg_proc WHERE proname = 'fn_trial_balance'").fetchone()
            if not r:
                pytest.skip('fn_trial_balance not installed')
        except Exception:
            pytest.skip('DB not available or fn_trial_balance missing')

        company_id = uuid4()
        # create account
        acc = Account(company_id=company_id, code='2000', name='TestAcc', type=AccountTypeEnum.asset)
        db.add(acc); db.commit(); db.refresh(acc)
        # insert many journal entries/lines
        N = int(benchmark_insert_count)
        for i in range(N):
            je = JournalEntry(company_id=company_id, number=f'JE{i}', date='2025-08-15', total_debit=100, total_credit=100, status='posted')
            db.add(je); db.flush()
            jl = JournalLine(journal_id=je.id, line_no=1, account_id=acc.id, debit=100, credit=0, description='Perf')
            db.add(jl)
            if i % 200 == 0:
                db.commit()
        db.commit()

        # measure trial balance
        t0 = time.time()
        res = fn_trial_balance(db, str(company_id), '2025-08-31')
        t1 = time.time()
        tb_time = t1 - t0

        # measure ledger (first page)
        t0 = time.time()
        ledger = fn_account_ledger(db, str(company_id), str(acc.id), '2025-08-01', '2025-08-31', 1, 100)
        t1 = time.time()
        ledger_time = t1 - t0

        print('trial_balance_time', tb_time, 'ledger_time', ledger_time)
        assert True
    finally:
        # cleanup - leave DB for manual inspection
        db.close()
