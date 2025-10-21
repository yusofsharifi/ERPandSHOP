from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID, uuid4
from typing import List, Optional
from app.models.treasury import CashAccount, BankAccount, TreasuryTransaction, BankReconciliation
from app.schemas import treasury as tr_schemas
import sqlalchemy as sa

class TreasuryService:
    @staticmethod
    def list_cash_accounts(db: Session) -> List[CashAccount]:
        return db.query(CashAccount).order_by(CashAccount.name).all()

    @staticmethod
    def create_cash_account(db: Session, payload: tr_schemas.CashAccountCreate) -> CashAccount:
        ca = CashAccount(name=payload.name, code=payload.code, currency=payload.currency, balance=payload.balance)
        db.add(ca)
        db.commit()
        db.refresh(ca)
        return ca

    @staticmethod
    def list_bank_accounts(db: Session) -> List[BankAccount]:
        return db.query(BankAccount).order_by(BankAccount.bank_name).all()

    @staticmethod
    def create_bank_account(db: Session, payload: tr_schemas.BankAccountCreate) -> BankAccount:
        ba = BankAccount(bank_name=payload.bank_name, account_number=payload.account_number, currency=payload.currency, balance=payload.balance)
        db.add(ba)
        db.commit()
        db.refresh(ba)
        return ba

    @staticmethod
    def transfer(db: Session, payload: tr_schemas.TreasuryTransactionCreate) -> TreasuryTransaction:
        # perform atomic transfer using SELECT FOR UPDATE
        with db.begin():
            # lock source and target rows depending on types
            if payload.source_type == 'cash':
                src = db.query(CashAccount).filter(CashAccount.id == payload.source_id).with_for_update().first()
            else:
                src = db.query(BankAccount).filter(BankAccount.id == payload.source_id).with_for_update().first()
            if payload.target_type == 'cash':
                tgt = db.query(CashAccount).filter(CashAccount.id == payload.target_id).with_for_update().first()
            else:
                tgt = db.query(BankAccount).filter(BankAccount.id == payload.target_id).with_for_update().first()

            if src is None or tgt is None:
                raise KeyError('account_not_found')
            amt = Decimal(payload.amount)
            if getattr(src, 'balance') is None:
                src.balance = Decimal('0.00')
            if getattr(tgt, 'balance') is None:
                tgt.balance = Decimal('0.00')
            # check sufficient funds
            if Decimal(src.balance) < amt:
                raise ValueError('insufficient_funds')
            # apply
            src.balance = Decimal(src.balance) - amt
            tgt.balance = Decimal(tgt.balance) + amt
            # create transaction record
            tx = TreasuryTransaction(
                source_type=payload.source_type,
                source_id=payload.source_id,
                target_type=payload.target_type,
                target_id=payload.target_id,
                amount=payload.amount,
                currency=payload.currency,
                date=payload.date,
                reference=payload.reference,
                created_by=payload.created_by,
            )
            db.add(tx)
            db.add(src)
            db.add(tgt)
            # commit happens on context exit
        # refresh tx
        db.refresh(tx)
        return tx

    @staticmethod
    def list_transactions(db: Session, limit: int = 100):
        return db.query(TreasuryTransaction).order_by(TreasuryTransaction.date.desc()).limit(limit).all()

    @staticmethod
    def create_bank_reconciliation(db: Session, payload: tr_schemas.BankReconciliationCreate) -> BankReconciliation:
        rec = BankReconciliation(bank_account_id=payload.bank_account_id, period_start=payload.period_start, period_end=payload.period_end, reconciliation_data=payload.reconciliation_data)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec


treasury_service = TreasuryService()
