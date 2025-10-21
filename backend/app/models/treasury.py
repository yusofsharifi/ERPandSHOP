import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    Integer,
    Numeric,
    ForeignKey,
    JSON,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base


class SourceTypeEnum(str, enum.Enum):
    cash = "cash"
    bank = "bank"


class ReconStatusEnum(str, enum.Enum):
    pending = "pending"
    reconciled = "reconciled"
    failed = "failed"


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(64), nullable=True)
    balance = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(16), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_cash_accounts_code", "code"),
    )


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = Column(String(255), nullable=False)
    account_number = Column(String(128), nullable=False)
    currency = Column(String(16), nullable=False, default="USD")
    balance = Column(Numeric(18, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_bank_accounts_account_number", "account_number"),
    )


class TreasuryTransaction(Base):
    __tablename__ = "treasury_transactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(PG_ENUM(SourceTypeEnum, name="source_type", create_type=False), nullable=False)
    source_id = Column(PGUUID(as_uuid=True), nullable=True)
    target_type = Column(PG_ENUM(SourceTypeEnum, name="target_type", create_type=False), nullable=False)
    target_id = Column(PGUUID(as_uuid=True), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(16), nullable=False, default="USD")
    date = Column(Date, nullable=False)
    reference = Column(String(255), nullable=True)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    check_id = Column(Integer, ForeignKey("checks.id", ondelete="SET NULL"), nullable=True)

    check = relationship("Check")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_treasury_tx_amount_positive"),
        Index("ix_treasury_transactions_date", "date"),
    )


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_account_id = Column(PGUUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(PG_ENUM(ReconStatusEnum, name="recon_status", create_type=False), nullable=False, default=ReconStatusEnum.pending)
    reconciliation_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    bank_account = relationship("BankAccount")

    __table_args__ = (
        Index("ix_bank_recon_bank_period", "bank_account_id", "period_start", "period_end"),
    )
