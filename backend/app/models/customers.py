import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Boolean, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    customer_no = Column(String(32), nullable=False)
    national_id = Column(String(64), nullable=True)
    registration_no = Column(String(64), nullable=True)
    credit_limit = Column(Numeric(18, 2), nullable=False, default=0)
    status = Column(String(32), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    partner = relationship("Partner")
    contacts = relationship("CustomerContact", cascade="all, delete-orphan", back_populates="customer")
    notes = relationship("CustomerNote", cascade="all, delete-orphan", back_populates="customer")
    transactions = relationship("CustomerTransaction", cascade="all, delete-orphan", back_populates="customer")

    __table_args__ = (
        UniqueConstraint('company_id', 'customer_no', name='uq_customers_company_customer_no'),
        Index('ix_customers_company_id', 'company_id'),
    )


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(PGUUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_name = Column(String(255), nullable=False)
    position = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="contacts")


class CustomerNote(Base):
    __tablename__ = "customer_notes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(PGUUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    note = Column(String, nullable=False)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="notes")


class CustomerTransaction(Base):
    __tablename__ = "customer_transactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(PGUUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    transaction_type = Column(String(32), nullable=False)  # invoice/payment/adjustment
    reference_id = Column(PGUUID(as_uuid=True), nullable=True)
    date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="transactions")
