import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Integer, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    order_no = Column(String(64), nullable=True)
    customer_id = Column(PGUUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False, index=True)
    date = Column(Date, nullable=False, default=date.today)
    expected_delivery_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    total_amount = Column(Numeric(18,2), nullable=False, default=0)
    total_discount = Column(Numeric(18,2), nullable=False, default=0)
    total_tax = Column(Numeric(18,2), nullable=False, default=0)
    net_amount = Column(Numeric(18,2), nullable=False, default=0)
    notes = Column(String, nullable=True)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lines = relationship("SalesOrderLine", cascade="all, delete-orphan", back_populates="order")

    __table_args__ = (
        Index('ix_sales_orders_order_no', 'order_no'),
    )


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(PGUUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Numeric(18,4), nullable=False, default=1)
    unit_price = Column(Numeric(18,4), nullable=False, default=0)
    discount = Column(Numeric(18,2), nullable=False, default=0)
    tax_rate = Column(Numeric(5,2), nullable=False, default=0)
    line_total = Column(Numeric(18,2), nullable=False, default=0)

    order = relationship("SalesOrder", back_populates="lines")
