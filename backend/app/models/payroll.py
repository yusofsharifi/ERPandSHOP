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
    UniqueConstraint,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base


class PayrollStatusEnum(str, enum.Enum):
    draft = 'draft'
    computed = 'computed'
    posted = 'posted'


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    national_id = Column(String(64), nullable=True, index=True)
    employment_no = Column(String(64), nullable=True, unique=True)
    bank_account = Column(String(128), nullable=True)
    hire_date = Column(Date, nullable=True)
    department_id = Column(PGUUID(as_uuid=True), nullable=True)
    tax_code = Column(String(64), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    payroll_lines = relationship("PayrollLine", back_populates="employee")

    __table_args__ = (
        Index('ix_employees_national_id', 'national_id'),
    )


class SalaryStructure(Base):
    __tablename__ = 'salary_structures'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    base_salary = Column(Numeric(18, 2), nullable=False, default=0)
    allowances = Column(JSONB, nullable=True)
    deductions = Column(JSONB, nullable=True)
    taxable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class PayrollRun(Base):
    __tablename__ = 'payroll_runs'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(PG_ENUM(PayrollStatusEnum, name='payroll_status', create_type=False), nullable=False, default=PayrollStatusEnum.draft)
    manager_approved = Column(Boolean, nullable=False, default=False)
    manager_approved_by = Column(PGUUID(as_uuid=True), nullable=True)
    manager_approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    lines = relationship("PayrollLine", back_populates="payroll", cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_payroll_runs_period', 'period_start', 'period_end'),
    )


class PayrollLine(Base):
    __tablename__ = 'payroll_lines'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(PGUUID(as_uuid=True), ForeignKey('payroll_runs.id', ondelete='CASCADE'), nullable=False, index=True)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    gross = Column(Numeric(18,2), nullable=False, default=0)
    taxes = Column(Numeric(18,2), nullable=False, default=0)
    deductions = Column(Numeric(18,2), nullable=False, default=0)
    net = Column(Numeric(18,2), nullable=False, default=0)
    components = Column(JSONB, nullable=True)  # snapshot of salary components
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    payroll = relationship("PayrollRun", back_populates="lines")
    employee = relationship("Employee", back_populates="payroll_lines")

    __table_args__ = (
        UniqueConstraint('employee_id', 'period_start', 'period_end', name='uq_payroll_line_employee_period'),
        CheckConstraint('gross >= 0', name='ck_payroll_line_gross_non_negative'),
        CheckConstraint('net >= 0', name='ck_payroll_line_net_non_negative'),
    )


class PayrollJournalLink(Base):
    __tablename__ = 'payroll_journal_links'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_run_id = Column(PGUUID(as_uuid=True), ForeignKey('payroll_runs.id', ondelete='CASCADE'), nullable=False, index=True)
    journal_entry_id = Column(PGUUID(as_uuid=True), ForeignKey('journal_entries.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    payroll_run = relationship('PayrollRun')

    __table_args__ = (
        Index('ix_payroll_journal_run', 'payroll_run_id'),
    )


class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    hours_worked = Column(Numeric(10,2), nullable=True, default=0)
    absence_days = Column(Numeric(10,2), nullable=True, default=0)
    overtime_hours = Column(Numeric(10,2), nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    employee = relationship('Employee')


class PayrollRule(Base):
    __tablename__ = 'payroll_rules'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False)  # e.g. 'tax', 'social'
    expression = Column(String, nullable=False)  # e.g. '0.10 * gross'
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_payroll_rules_type', 'rule_type'),
    )
