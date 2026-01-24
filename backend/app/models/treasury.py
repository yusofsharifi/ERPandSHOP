import enum
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    Integer,
    Numeric,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    JSON,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ENUM as PG_ENUM, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class TreasurySourceTypeEnum(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    other = "other"


class TreasuryTargetTypeEnum(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    other = "other"


class ReconciliationStatusEnum(str, enum.Enum):
    draft = "draft"
    matched = "matched"
    applied = "applied"


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    balance = Column(Numeric(18, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_cash_accounts_company_code', 'company_id', 'code'),
    )

    def apply_amount(self, db, amount: float):
        """Apply amount to the cash account balance (atomic when called inside transaction)."""
        # amount positive increases balance
        self.balance = float(self.balance or 0) + float(amount or 0)
        db.add(self)
        return self.balance

    def compute_balance(self, db):
        """Return stored balance. Services should reconcile using transactions."""
        return float(self.balance or 0)


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    bank_name = Column(String(255), nullable=False)
    account_number = Column(String(64), nullable=False)
    iban = Column(String(64), nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    balance = Column(Numeric(18, 2), nullable=False, default=0)
    routing_code = Column(String(64), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_bank_accounts_company_account', 'company_id', 'account_number'),
    )

    def apply_amount(self, db, amount: float):
        self.balance = float(self.balance or 0) + float(amount or 0)
        db.add(self)
        return self.balance

    def compute_balance(self, db):
        return float(self.balance or 0)


class TreasuryTransaction(Base):
    __tablename__ = "treasury_transactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    source_type = Column(PG_ENUM(TreasurySourceTypeEnum, name='treasury_source_type', create_type=False), nullable=False)
    source_id = Column(PGUUID(as_uuid=True), nullable=True)
    target_type = Column(PG_ENUM(TreasuryTargetTypeEnum, name='treasury_target_type', create_type=False), nullable=False)
    target_id = Column(PGUUID(as_uuid=True), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    exchange_rate = Column(Numeric(18, 6), nullable=False, default=1)
    date = Column(DateTime(timezone=True), nullable=False)
    reference = Column(String(255), nullable=True)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    posted = Column(Boolean, nullable=False, default=False)
    journal_entry_id = Column(PGUUID(as_uuid=True), ForeignKey('journal_entries.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_treasury_transactions_company_date', 'company_id', 'date'),
        Index('ix_treasury_transactions_posted', 'posted'),
    )

    def apply(self, db, post_journal: bool = True, journal_entry_id: uuid.UUID = None):
        """
        Apply transaction: debit source and credit target. Must be called inside a DB transaction/session.
        For cash/bank source/target, fetch the account row FOR UPDATE in the service layer before calling this.
        """
        amt = float(self.amount or 0)
        # handle source
        if self.source_type == TreasurySourceTypeEnum.cash and self.source_id:
            from app.models.treasury import CashAccount as _Cash
            acc = db.query(_Cash).filter(_Cash.id == self.source_id).with_for_update().first()
            if not acc:
                raise KeyError('source_account_not_found')
            acc.apply_amount(db, -amt)
        elif self.source_type == TreasurySourceTypeEnum.bank and self.source_id:
            from app.models.treasury import BankAccount as _Bank
            acc = db.query(_Bank).filter(_Bank.id == self.source_id).with_for_update().first()
            if not acc:
                raise KeyError('source_account_not_found')
            acc.apply_amount(db, -amt)

        # handle target
        if self.target_type == TreasuryTargetTypeEnum.cash and self.target_id:
            from app.models.treasury import CashAccount as _Cash
            acc = db.query(_Cash).filter(_Cash.id == self.target_id).with_for_update().first()
            if not acc:
                raise KeyError('target_account_not_found')
            acc.apply_amount(db, amt)
        elif self.target_type == TreasuryTargetTypeEnum.bank and self.target_id:
            from app.models.treasury import BankAccount as _Bank
            acc = db.query(_Bank).filter(_Bank.id == self.target_id).with_for_update().first()
            if not acc:
                raise KeyError('target_account_not_found')
            acc.apply_amount(db, amt)

        # mark posted and attach journal entry if provided
        if post_journal:
            self.posted = True
            if journal_entry_id:
                self.journal_entry_id = journal_entry_id
        db.add(self)
        return True

    def rollback_effects(self, db):
        """Reverse the balance effects of this transaction. Intended for rare rollbacks; must be called transactionally."""
        amt = float(self.amount or 0)
        # reverse: credit source, debit target
        if self.source_type == TreasurySourceTypeEnum.cash and self.source_id:
            from app.models.treasury import CashAccount as _Cash
            acc = db.query(_Cash).filter(_Cash.id == self.source_id).with_for_update().first()
            if acc:
                acc.apply_amount(db, amt)
        if self.source_type == TreasurySourceTypeEnum.bank and self.source_id:
            from app.models.treasury import BankAccount as _Bank
            acc = db.query(_Bank).filter(_Bank.id == self.source_id).with_for_update().first()
            if acc:
                acc.apply_amount(db, amt)
        if self.target_type == TreasuryTargetTypeEnum.cash and self.target_id:
            from app.models.treasury import CashAccount as _Cash
            acc = db.query(_Cash).filter(_Cash.id == self.target_id).with_for_update().first()
            if acc:
                acc.apply_amount(db, -amt)
        if self.target_type == TreasuryTargetTypeEnum.bank and self.target_id:
            from app.models.treasury import BankAccount as _Bank
            acc = db.query(_Bank).filter(_Bank.id == self.target_id).with_for_update().first()
            if acc:
                acc.apply_amount(db, -amt)
        # unpost
        self.posted = False
        db.add(self)
        return True


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    bank_account_id = Column(PGUUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(PG_ENUM(ReconciliationStatusEnum, name='reconciliation_status', create_type=False), nullable=False, default=ReconciliationStatusEnum.draft)
    reconciliation_data = Column(JSONB, nullable=True)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    applied_by = Column(PGUUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_bank_recon_account_period', 'bank_account_id', 'period_start', 'period_end'),
    )


class BankStatementLine(Base):
    __tablename__ = "bank_statement_lines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reconciliation_id = Column(PGUUID(as_uuid=True), ForeignKey('bank_reconciliations.id'), nullable=True)
    bank_account_id = Column(PGUUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=False, index=True)
    statement_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    reference = Column(String(255), nullable=True)
    matched = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index('ix_bank_statement_lines_account_date', 'bank_account_id', 'statement_date'),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
    actor_id = Column(PGUUID(as_uuid=True), nullable=True)
    action = Column(String(128), nullable=False)
    object_type = Column(String(64), nullable=True)
    object_id = Column(PGUUID(as_uuid=True), nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_audit_logs_company_action', 'company_id', 'action'),
    )
