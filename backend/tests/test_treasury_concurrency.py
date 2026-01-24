import threading
import time
import pytest
from uuid import uuid4
from app.db.session import SessionLocal
from app.models.treasury import CashAccount, BankAccount
from app.services.treasury_service import transfer_funds


def setup_account_pair(db):
    comp = uuid4()
    c = CashAccount(id=uuid4(), company_id=comp, code='C1', name='Cash1', currency='USD', balance=1000)
    b = BankAccount(id=uuid4(), company_id=comp, bank_name='Bank1', account_number='111', currency='USD', balance=1000)
    db.add(c); db.add(b); db.commit()
    return comp, c, b


def test_concurrent_transfers():
    db_main = SessionLocal()
    try:
        comp, c, b = setup_account_pair(db_main)
    finally:
        db_main.close()

    results = []
    start_evt = threading.Event()

    def worker(amount, out_list):
        db = SessionLocal()
        try:
            start_evt.wait()
            try:
                transfer_funds(db, company_id=comp, payload={'from_type':'cash','from_id':str(c.id),'to_type':'bank','to_id':str(b.id),'amount':amount,'currency':'USD'}, performed_by=None)
                out_list.append('ok')
            except Exception as e:
                out_list.append(('err', str(e)))
        finally:
            db.close()

    t1_res = []
    t2_res = []
    t1 = threading.Thread(target=worker, args=(800, t1_res))
    t2 = threading.Thread(target=worker, args=(800, t2_res))
    t1.start(); t2.start()
    time.sleep(0.1)
    start_evt.set()
    t1.join(); t2.join()

    # Refresh final balances
    db_final = SessionLocal()
    try:
        final_cash = db_final.query(CashAccount).filter(CashAccount.id == c.id).first()
        final_bank = db_final.query(BankAccount).filter(BankAccount.id == b.id).first()
        assert final_cash is not None and final_bank is not None
        # Only one transfer should have succeeded (1000 - 800 = 200)
        assert float(final_cash.balance) == pytest.approx(200.0)
        assert float(final_bank.balance) == pytest.approx(1800.0)
        # One thread must have failed
        assert (t1_res and t2_res) and (('ok' in t1_res) ^ ('ok' in t2_res))
    finally:
        db_final.close()
