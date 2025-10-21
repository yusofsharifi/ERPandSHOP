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
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base


class PartnerTypeEnum(str, enum.Enum):
    customer = "customer"
    supplier = "supplier"


class InvoiceStatusEnum(str, enum.Enum):
    draft = "draft"
    open = "open"
    paid = "paid"
    cancelled = "cancelled"
    partial = "partial"


class InvoiceTypeEnum(str, enum.Enum):
    sale = "sale"
    purchase = "purchase"


class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    check = "check"
    gateway = "gateway"


class CheckStatusEnum(str, enum.Enum):
    issued = "issued"
    deposited = "deposited"
    bounced = "bounced"
    cleared = "cleared"


class Partner(Base):
    __tablename__ = "partners"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    partner_type = Column(PG_ENUM(PartnerTypeEnum, name="partner_type", create_type=False), nullable=False)
    tax_id = Column(String(64), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String, nullable=True)
    credit_limit = Column(Numeric(18, 2), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    invoices = relationship("Invoice", back_populates="partner")
    payments = relationship("Payment", back_populates="partner")

    __table_args__ = (
        Index("ix_partners_name", "name"),
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_no = Column(String(64), nullable=False, index=True)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(18, 2), nullable=False, default=0)
    balance_amount = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(16), nullable=False, default="USD")
    status = Column(PG_ENUM(InvoiceStatusEnum, name="invoice_status", create_type=False), nullable=False, default=InvoiceStatusEnum.draft)
    invoice_type = Column(PG_ENUM(InvoiceTypeEnum, name="invoice_type", create_type=False), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    partner = relationship("Partner", back_populates="invoices")
    lines = relationship("InvoiceLine", cascade="all, delete-orphan", back_populates="invoice", order_by="InvoiceLine.id")
    payments = relationship("Payment", back_populates="invoice")

    __table_args__ = (
        Index("ix_invoices_date", "date"),
        UniqueConstraint("invoice_no", name="uq_invoices_invoice_no"),
        CheckConstraint("total_amount >= 0", name="ck_invoice_total_non_negative"),
        CheckConstraint("balance_amount >= 0", name="ck_invoice_balance_non_negative"),
    )


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(PGUUID(as_uuid=True), nullable=True)
    description = Column(String, nullable=True)
    qty = Column(Numeric(18, 4), nullable=False, default=1)
    unit_price = Column(Numeric(18, 4), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0)  # e.g. 0.09 for 9%
    line_total = Column(Numeric(18, 2), nullable=False, default=0)

    invoice = relationship("Invoice", back_populates="lines")

    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_invoice_line_qty_non_negative"),
        CheckConstraint("unit_price >= 0", name="ck_invoice_line_price_non_negative"),
        CheckConstraint("tax_rate >= 0", name="ck_invoice_line_tax_non_negative"),
        CheckConstraint("line_total >= 0", name="ck_invoice_line_total_non_negative"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    method = Column(PG_ENUM(PaymentMethodEnum, name="payment_method", create_type=False), nullable=False)
    payment_date = Column(Date, nullable=False)
    reference = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
    partner = relationship("Partner", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_amount_positive"),
        Index("ix_payments_date", "payment_date"),
    )


class Check(Base):
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    check_no = Column(String(64), nullable=False)
    bank = Column(String(128), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(PG_ENUM(CheckStatusEnum, name="check_status", create_type=False), nullable=False, default=CheckStatusEnum.issued)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_check_amount_positive"),
        UniqueConstraint("check_no", name="uq_checks_check_no"),
        Index("ix_checks_due_date", "due_date"),
    )
