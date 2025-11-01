import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    Numeric,
    ForeignKey,
    JSON,
    Text,
    UniqueConstraint,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContractTypeEnum(str, enum.Enum):
    permanent = "permanent"
    contract = "contract"
    part_time = "part_time"
    hourly = "hourly"


class PayrollStatusEnum(str, enum.Enum):
    draft = "draft"
    validated = "validated"
    closed = "closed"


class PaymentStatusEnum(str, enum.Enum):
    unpaid = "unpaid"
    in_progress = "in_progress"
    paid = "paid"


class PayrollLineTypeEnum(str, enum.Enum):
    earning = "earning"
    deduction = "deduction"


# Employees
class Employee(Base):
    __tablename__ = "employees"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    employee_code = Column(String(64), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    national_id = Column(String(64), nullable=True, index=True)
    job_title = Column(String(255), nullable=True)
    department_id = Column(PGUUID(as_uuid=True), nullable=True)
    hire_date = Column(Date, nullable=True)
    contract_type = Column(PG_ENUM(ContractTypeEnum, name="contract_type", create_type=False), nullable=False)
    base_salary = Column(Numeric(18, 2), nullable=False, default=0)
    bank_account = Column(String(128), nullable=True)
    iban = Column(String(64), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payrolls = relationship("Payroll", back_populates="employee")

    __table_args__ = (
        Index("ix_employees_national_id", "national_id"),
    )


# Salary structures
class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    currency = Column(String(3), nullable=False, default="IRR")
    rules = Column(JSONB, nullable=True)  # list of components {code,name,type,amount,formula}
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payrolls = relationship("Payroll", back_populates="structure")


# Payroll periods
class PayrollPeriod(Base):
    __tablename__ = "payroll_periods"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(PG_ENUM(PayrollStatusEnum, name="payroll_status", create_type=False), nullable=False, default=PayrollStatusEnum.draft)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payrolls = relationship("Payroll", back_populates="period")

    __table_args__ = (
        Index("ix_payroll_periods_company_start_end", "company_id", "start_date", "end_date"),
    )


# Payroll header
class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    period_id = Column(PGUUID(as_uuid=True), ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False, index=True)
    structure_id = Column(PGUUID(as_uuid=True), ForeignKey("salary_structures.id", ondelete="SET NULL"), nullable=True)
    gross_salary = Column(Numeric(18, 2), nullable=False, default=0)
    total_deductions = Column(Numeric(18, 2), nullable=False, default=0)
    net_salary = Column(Numeric(18, 2), nullable=False, default=0)
    payment_status = Column(PG_ENUM(PaymentStatusEnum, name="payment_status", create_type=False), nullable=False, default=PaymentStatusEnum.unpaid)
    journal_entry_id = Column(PGUUID(as_uuid=True), nullable=True)
    pay_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="payrolls")
    period = relationship("PayrollPeriod", back_populates="payrolls")
    structure = relationship("SalaryStructure", back_populates="payrolls")
    lines = relationship("PayrollLine", back_populates="payroll", cascade="all, delete-orphan")
    deductions = relationship("Deduction", back_populates="payroll", cascade="all, delete-orphan")
    bonuses = relationship("Bonus", back_populates="payroll", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("employee_id", "period_id", name="uq_payroll_employee_period"),
        Index("ix_payrolls_employee_period_status", "employee_id", "period_id", "payment_status"),
    )


# Payroll lines
class PayrollLine(Base):
    __tablename__ = "payroll_lines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(PGUUID(as_uuid=True), ForeignKey("payrolls.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(PG_ENUM(PayrollLineTypeEnum, name="payroll_line_type", create_type=False), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False, default=0)
    formula = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payroll = relationship("Payroll", back_populates="lines")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payroll_line_amount_non_negative"),
    )


# Deductions
class Deduction(Base):
    __tablename__ = "deductions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(PGUUID(as_uuid=True), ForeignKey("payrolls.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(64), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payroll = relationship("Payroll", back_populates="deductions")


# Bonuses
class Bonus(Base):
    __tablename__ = "bonuses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(PGUUID(as_uuid=True), ForeignKey("payrolls.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(64), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payroll = relationship("Payroll", back_populates="bonuses")
