import pytest
from app.db.session import SessionLocal
from app.models.treasury import CashAccount, BankAccount, TreasuryTransaction
from app.services.treasury_service import transfer_funds
from uuid import uuid4


def setup_accounts(db):
    comp = uuid4()
    c = CashAccount(id=uuid4(), company_id=comp, code='C1', name='Cash1', currency='USD', balance=1000)
    b = BankAccount(id=uuid4(), company_id=comp, bank_name='Bank1', account_number='111', currency='USD', balance=2000)
    db.add(c); db.add(b); db.commit()
    return comp, c, b


def test_transfer_success():
    db = SessionLocal()
    try:
        comp, c, b = setup_accounts(db)
        payload = {'from_type':'bank','from_id':str(b.id),'to_type':'cash','to_id':str(c.id),'amount':500,'currency':'USD'}
        txn = transfer_funds(db, company_id=comp, payload=payload, performed_by=None)
        # fetch accounts
        db.refresh(c); db.refresh(b)
        assert float(c.balance) == 1500.0
        assert float(b.balance) == 1500.0
        assert isinstance(txn, TreasuryTransaction)
    finally:
        db.close()


def test_insufficient_funds():
    db = SessionLocal()
    try:
        comp, c, b = setup_accounts(db)
        payload = {'from_type':'cash','from_id':str(c.id),'to_type':'bank','to_id':str(b.id),'amount':99999,'currency':'USD'}
        with pytest.raises(Exception):
            transfer_funds(db, company_id=comp, payload=payload, performed_by=None)
    finally:
        db.close()
