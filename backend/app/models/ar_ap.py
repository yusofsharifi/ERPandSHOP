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
    partial = "partial"
    paid = "paid"
    cancelled = "cancelled"


class InvoiceTypeEnum(str, enum.Enum):
    sale = "sale"
    purchase = "purchase"


class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    check = "check"
    gateway = "gateway"
    other = "other"


class CheckStatusEnum(str, enum.Enum):
    issued = "issued"
    received = "received"
    deposited = "deposited"
    cleared = "cleared"
    bounced = "bounced"
    returned = "returned"


class Partner(Base):
    __tablename__ = "partners"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    partner_type = Column(PG_ENUM(PartnerTypeEnum, name="partner_type", create_type=False), nullable=False)
    tax_id = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    address = Column(String, nullable=True)
    credit_limit = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default='USD')
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
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_no = Column(String(64), nullable=False)
    series = Column(String(8), nullable=True, default='')
    invoice_type = Column(PG_ENUM(InvoiceTypeEnum, name="invoice_type", create_type=False), nullable=False)
    date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    subtotal = Column(Numeric(18, 2), nullable=False, default=0)
    tax_total = Column(Numeric(18, 2), nullable=False, default=0)
    total_amount = Column(Numeric(18, 2), nullable=False, default=0)
    balance_amount = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    exchange_rate = Column(Numeric(18, 6), nullable=False, default=1)
    status = Column(PG_ENUM(InvoiceStatusEnum, name="invoice_status", create_type=False), nullable=False, default=InvoiceStatusEnum.draft)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    partner = relationship("Partner", back_populates="invoices")
    lines = relationship("InvoiceLine", cascade="all, delete-orphan", back_populates="invoice", order_by="InvoiceLine.line_no")
    payments = relationship("Payment", back_populates="invoice")

    __table_args__ = (
        Index("ix_invoices_date", "date"),
        Index("ix_invoices_due_date", "due_date"),
        UniqueConstraint("company_id", "series", "invoice_no", name="uq_invoices_company_series_no"),
        CheckConstraint("total_amount >= 0", name="ck_invoice_total_non_negative"),
        CheckConstraint("balance_amount >= 0", name="ck_invoice_balance_non_negative"),
    )

    def recalc_totals(self):
        # recompute subtotal, tax_total, total_amount from lines
        subtotal = 0
        tax_total = 0
        for ln in self.lines:
            subtotal += float(ln.qty or 0) * float(ln.unit_price or 0)
            tax_total += float(ln.line_total or 0) - (float(ln.qty or 0) * float(ln.unit_price or 0))
        self.subtotal = round(subtotal, 2)
        self.tax_total = round(tax_total, 2)
        self.total_amount = round(self.subtotal + self.tax_total, 2)


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    line_no = Column(Integer, nullable=False)
    product_id = Column(PGUUID(as_uuid=True), nullable=True)
    description = Column(String, nullable=True)
    qty = Column(Numeric(18, 4), nullable=False, default=1)
    unit_price = Column(Numeric(18, 4), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)  # percent 9.00
    line_total = Column(Numeric(18, 4), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="lines")

    __table_args__ = (
        UniqueConstraint("invoice_id", "line_no", name="uq_invoice_lines_invoice_line_no"),
        CheckConstraint("qty >= 0", name="ck_invoice_line_qty_non_negative"),
        CheckConstraint("unit_price >= 0", name="ck_invoice_line_price_non_negative"),
        CheckConstraint("tax_rate >= 0", name="ck_invoice_line_tax_non_negative"),
        CheckConstraint("line_total >= 0", name="ck_invoice_line_total_non_negative"),
    )

    def compute_line_total(self):
        amt = float(self.qty or 0) * float(self.unit_price or 0)
        tax = amt * (float(self.tax_rate or 0) / 100)
        self.line_total = round(amt + tax, 4)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    method = Column(PG_ENUM(PaymentMethodEnum, name="payment_method", create_type=False), nullable=False)
    reference = Column(String(128), nullable=True)
    date = Column(Date, nullable=False)
    posted = Column(Boolean, nullable=False, default=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
    partner = relationship("Partner", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_amount_positive"),
        Index("ix_payments_date", "date"),
    )


class Check(Base):
    __tablename__ = "checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="SET NULL"), nullable=True)
    check_no = Column(String(64), nullable=False)
    bank_name = Column(String(128), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(PG_ENUM(CheckStatusEnum, name="check_status", create_type=False), nullable=False, default=CheckStatusEnum.issued)
    related_payment_id = Column(PGUUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_check_amount_positive"),
        UniqueConstraint("company_id", "check_no", name="uq_checks_company_check_no"),
        Index("ix_checks_due_date", "due_date"),
    )


# materialized view partner_ledger_view can be created in Alembic migration
