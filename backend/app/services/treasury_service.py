from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from decimal import Decimal
from app.db.session import SessionLocal
from app.models.treasury import CashAccount, BankAccount, TreasuryTransaction, AuditLog
from app.services import gl_service
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


def transfer_funds(db: Session, company_id: UUID, payload: Dict[str, Any], performed_by: Optional[UUID] = None):
    """
    Perform a transfer between two accounts. Uses row-level locking on involved accounts.
    payload: { from_type, from_id, to_type, to_id, amount, currency, exchange_rate, date, reference, allow_overdraft }
    """
    amt = Decimal(str(payload.get('amount', 0)))
    if amt <= 0:
        raise ValueError('invalid_amount')

    from_type = payload.get('from_type')
    to_type = payload.get('to_type')
    from_id = payload.get('from_id')
    to_id = payload.get('to_id')
    currency = payload.get('currency', 'USD')
    exchange_rate = Decimal(str(payload.get('exchange_rate', 1))) if payload.get('exchange_rate') else Decimal('1')
    allow_overdraft = bool(payload.get('allow_overdraft', False))
    date = payload.get('date') or datetime.utcnow()
    reference = payload.get('reference')

    try:
        # lock source and target depending on type
        src_acc = None
        tgt_acc = None
        if from_type == 'cash' and from_id:
            src_acc = db.query(CashAccount).filter(CashAccount.id == from_id).with_for_update().first()
        elif from_type == 'bank' and from_id:
            src_acc = db.query(BankAccount).filter(BankAccount.id == from_id).with_for_update().first()

        if to_type == 'cash' and to_id:
            tgt_acc = db.query(CashAccount).filter(CashAccount.id == to_id).with_for_update().first()
        elif to_type == 'bank' and to_id:
            tgt_acc = db.query(BankAccount).filter(BankAccount.id == to_id).with_for_update().first()

        if from_id and not src_acc:
            raise KeyError('source_not_found')
        if to_id and not tgt_acc:
            raise KeyError('target_not_found')

        # validate balance
        if src_acc and not allow_overdraft:
            if Decimal(str(src_acc.balance or 0)) < amt:
                raise ValueError('insufficient_funds')

        # create treasury transaction
        txn = TreasuryTransaction(
            company_id=company_id,
            source_type=from_type,
            source_id=from_id,
            target_type=to_type,
            target_id=to_id,
            amount=amt,
            currency=currency,
            exchange_rate=exchange_rate,
            date=date,
            reference=reference,
            posted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(txn)
        db.flush()  # ensure id

        # apply balances
        # debit source
        if src_acc:
            src_acc.apply_amount(db, -float(amt))
        # credit target
        if tgt_acc:
            tgt_acc.apply_amount(db, float(amt))

        # create GL journal entry via gl_service (integration)
        try:
            je = gl_service.create_journal_entry(db, company_id=company_id, date=date, lines=[
                # simple two-line entry; in real integration use proper accounts
                {'account': 'treasury:source', 'debit': float(amt), 'credit': 0},
                {'account': 'treasury:target', 'debit': 0, 'credit': float(amt)},
            ], reference=reference, created_by=performed_by)
            txn.posted = True
            txn.journal_entry_id = je.id if je else None
        except Exception:
            # If GL fails, mark transaction as not posted but keep treasury txn for investigation
            txn.posted = False

        # audit log
        al = AuditLog(company_id=company_id, actor_id=performed_by, action='treasury.transfer', object_type='treasury_transaction', object_id=txn.id, payload={'from': str(from_id), 'to': str(to_id), 'amount': float(amt), 'currency': currency, 'reference': reference})
        db.add(al)

        db.commit()
        db.refresh(txn)
        return txn
    except SQLAlchemyError as e:
        db.rollback()
        raise


def list_accounts(db: Session, acc_type: Optional[str] = None, company_id: Optional[UUID] = None):
    res = []
    if acc_type == 'cash' or acc_type is None:
        res.extend(db.query(CashAccount).filter(CashAccount.company_id == company_id).all())
    if acc_type == 'bank' or acc_type is None:
        res.extend(db.query(BankAccount).filter(BankAccount.company_id == company_id).all())
    return res


def get_account(db: Session, acc_id: UUID):
    acc = db.query(CashAccount).filter(CashAccount.id == acc_id).first()
    if acc:
        return acc
    acc = db.query(BankAccount).filter(BankAccount.id == acc_id).first()
    return acc


def create_cash_account(db: Session, payload: Dict[str, Any]):
    acc = CashAccount(**payload)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


def create_bank_account(db: Session, payload: Dict[str, Any]):
    acc = BankAccount(**payload)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc
