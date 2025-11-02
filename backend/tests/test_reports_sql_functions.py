import pytest
from app.db.session import SessionLocal
from app.reports.reports_sql import fn_trial_balance
from decimal import Decimal
from uuid import uuid4
from app.models.gl_models import Account, JournalEntry, JournalLine
from app.models.gl_models import AccountTypeEnum
from app.models import gl_models


def has_fn(db):
    try:
        r = db.execute("SELECT proname FROM pg_proc WHERE proname = 'fn_trial_balance'").fetchone()
        return bool(r)
    except Exception:
        return False


@pytest.mark.skipif(False, reason="Will be skipped if fn_trial_balance not installed")
def test_fn_trial_balance_sample():
    db = SessionLocal()
    try:
        if not has_fn(db):
            pytest.skip("fn_trial_balance not present in DB; apply backend/sql/reports_views.sql and refresh")
        # create sample company id via company in journal entries (assume companies table exists)
        company_id = uuid4()
        # create accounts
        acc = Account(company_id=company_id, code='4000', name='Sales', type=AccountTypeEnum.revenue)
        acc2 = Account(company_id=company_id, code='5000', name='COGS', type=AccountTypeEnum.cogs)
        db.add_all([acc, acc2])
        db.commit(); db.refresh(acc); db.refresh(acc2)
        # create journal entries and lines
        je = JournalEntry(company_id=company_id, number='JE1', date='2025-08-15', total_debit=1000, total_credit=1000, status='posted')
        db.add(je); db.commit(); db.refresh(je)
        jl1 = JournalLine(journal_id=je.id, line_no=1, account_id=acc.id, debit=0, credit=1000, description='Sale')
        jl2 = JournalLine(journal_id=je.id, line_no=2, account_id=acc2.id, debit=1000, credit=0, description='COGS')
        db.add_all([jl1, jl2])
        db.commit()
        # call fn_trial_balance
        res = fn_trial_balance(db, str(company_id), '2025-08-31')
        assert res is not None
        assert 'accounts' in res
        # find sales account
        sales = next((a for a in res['accounts'] if a['account_code'] == '4000'), None)
        assert sales is not None
        # closing balance for revenue account (credit > debit) should be negative or positive depending convention
    finally:
        # cleanup
        try:
            db.query(JournalLine).filter(JournalLine.journal_id == je.id).delete()
            db.query(JournalEntry).filter(JournalEntry.id == je.id).delete()
            db.query(Account).filter(Account.id.in_([acc.id, acc2.id])).delete()
            db.commit()
        except Exception:
            pass
        db.close()
