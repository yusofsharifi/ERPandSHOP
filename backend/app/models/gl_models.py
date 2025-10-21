from datetime import datetime
import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    Integer,
    BigInteger,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base


class AccountTypeEnum(str, enum.Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    expense = "expense"


class JournalStatusEnum(str, enum.Enum):
    draft = "draft"
    posted = "posted"
    cancelled = "cancelled"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    code = Column(String(128), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(PG_ENUM(AccountTypeEnum, name="account_type", create_type=False), nullable=False)
    parent_id = Column(PGUUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parent = relationship("Account", remote_side=[id], backref="children")

    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_accounts_company_code"),
        Index("ix_accounts_code", "code"),
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    number = Column(String(64), unique=True, nullable=True)
    date = Column(Date, nullable=False)
    # optional jalali_date can be computed/stored by app logic
    jalali_date = Column(String(32), nullable=True)
    description = Column(String, nullable=True)
    total_debit = Column(Numeric(18, 2), nullable=False)
    total_credit = Column(Numeric(18, 2), nullable=False)
    status = Column(PG_ENUM(JournalStatusEnum, name="journal_status", create_type=False), nullable=False, default=JournalStatusEnum.draft)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lines = relationship("JournalLine", cascade="all, delete-orphan", back_populates="journal", order_by="JournalLine.line_no")

    __table_args__ = (
        Index("ix_journal_entries_date", "date"),
        Index("ix_journal_entries_number", "number"),
        CheckConstraint("total_debit >= 0", name="ck_journal_total_debit_non_negative"),
        CheckConstraint("total_credit >= 0", name="ck_journal_total_credit_non_negative"),
    )


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(PGUUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    line_no = Column(Integer, nullable=False)
    account_id = Column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    debit = Column(Numeric(18, 2), nullable=False, default=0)
    credit = Column(Numeric(18, 2), nullable=False, default=0)
    description = Column(String, nullable=True)

    journal = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")

    __table_args__ = (
        UniqueConstraint("journal_id", "line_no", name="uq_journal_lines_journal_line_no"),
        CheckConstraint("debit >= 0", name="ck_journal_line_debit_non_negative"),
        CheckConstraint("credit >= 0", name="ck_journal_line_credit_non_negative"),
    )


class GlAutoNumber(Base):
    __tablename__ = "gl_auto_number"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year = Column(Integer, nullable=False)
    company_id = Column(PGUUID(as_uuid=True), nullable=False)
    last_number = Column(BigInteger, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("year", "company_id", name="uq_gl_auto_number_year_company"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(PGUUID(as_uuid=True), nullable=True)
    action = Column(String(50), nullable=False)
    payload = Column(JSONB, nullable=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=True)
    ts = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
    )
