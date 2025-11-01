from pydantic import BaseModel, condecimal, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime

Money = condecimal(max_digits=20, decimal_places=2)

# Employee schemas
class EmployeeRead(BaseModel):
    id: UUID
    company_id: UUID
    employee_code: str
    first_name: str
    last_name: str
    national_id: Optional[str]
    job_title: Optional[str]
    department_id: Optional[UUID]
    hire_date: Optional[date]
    contract_type: Optional[str]
    base_salary: Money
    bank_account: Optional[str]
    iban: Optional[str]
    is_active: bool

# Salary structure
class SalaryStructureCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = Field(..., min_length=3, max_length=3)
    rules: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = False

class SalaryStructureRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    currency: str
    rules: Optional[Dict[str, Any]]
    is_default: bool
    created_at: Optional[datetime]

# Payroll period
class PayrollPeriodCreate(BaseModel):
    company_id: UUID
    name: str
    start_date: date
    end_date: date

class PayrollPeriodRead(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    created_by: Optional[UUID]
    created_at: Optional[datetime]

# Payroll (per employee)
class PayrollCreate(BaseModel):
    employee_id: UUID
    period_id: UUID
    structure_id: Optional[UUID] = None

class PayrollRead(BaseModel):
    id: UUID
    employee_id: UUID
    period_id: UUID
    structure_id: Optional[UUID]
    gross_salary: Money
    total_deductions: Money
    net_salary: Money
    payment_status: str
    pay_date: Optional[date]
    created_at: Optional[datetime]

class PayrollLineRead(BaseModel):
    id: UUID
    payroll_id: UUID
    code: str
    name: str
    type: str
    amount: Money
    formula: Optional[str]

class DeductionRead(BaseModel):
    id: UUID
    payroll_id: UUID
    type: str
    amount: Money
    description: Optional[str]

class BonusRead(BaseModel):
    id: UUID
    payroll_id: UUID
    type: str
    amount: Money
    description: Optional[str]

# Compute response
class GenerateResponse(BaseModel):
    generated: int
    payrolls_created: int

# Simple
class SimpleResponse(BaseModel):
    code: str
    message: Dict[str, str]

# Report query
class PayrollReportQuery(BaseModel):
    company_id: Optional[UUID] = None
    period_id: Optional[UUID] = None
    department_id: Optional[UUID] = None

class PayrollReportRow(BaseModel):
    key: str
    gross: Money
    deductions: Money
    net: Money

class PayrollReportResponse(BaseModel):
    rows: List[PayrollReportRow]
    total_gross: Money
    total_deductions: Money
    total_net: Money
