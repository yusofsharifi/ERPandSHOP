from pydantic import BaseModel, condecimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date

Money = condecimal(max_digits=20, decimal_places=2)

class PayrollRunCreate(BaseModel):
    period_start: date
    period_end: date
    employee_ids: Optional[List[UUID]] = None

class PayrollRunRead(BaseModel):
    id: UUID
    period_start: date
    period_end: date
    generated_at: Optional[str]
    status: str

class PayrollLineRead(BaseModel):
    id: UUID
    payroll_id: UUID
    employee_id: UUID
    period_start: date
    period_end: date
    gross: Money
    taxes: Money
    deductions: Money
    net: Money
    components: Optional[Dict[str, Any]]

class PayrollComputeResponse(BaseModel):
    payroll_id: UUID
    lines_generated: int

class SimpleResponse(BaseModel):
    code: str
    message: Dict[str, str]
