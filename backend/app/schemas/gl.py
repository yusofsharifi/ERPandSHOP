from pydantic import BaseModel, condecimal, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

Money = condecimal(max_digits=20, decimal_places=2)

class AccountIn(BaseModel):
    company_id: UUID
    code: str
    name: str
    type: str
    parent_id: Optional[UUID] = None

class AccountOut(AccountIn):
    id: UUID
    is_active: bool = True
    created_at: Optional[str]
    updated_at: Optional[str]

class JournalLineIn(BaseModel):
    line_no: int
    account_id: UUID
    description: Optional[str] = None
    debit: Money = 0
    credit: Money = 0
    cost_center_id: Optional[UUID] = None
    analytic_tags: Optional[Dict[str, Any]] = None

    @validator("debit", "credit")
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("amount_must_be_non_negative")
        return v

    @validator("credit")
    def not_both_positive(cls, credit, values):
        debit = values.get("debit")
        if debit and debit > 0 and credit and credit > 0:
            raise ValueError("both_debit_credit")
        return credit

class JournalEntryCreate(BaseModel):
    company_id: UUID
    fiscal_year: int
    period: str
    date: date
    description: Optional[str] = None
    lines: List[JournalLineIn]
    attachments: Optional[List[str]] = []

    @validator("lines")
    def at_least_one_line(cls, v):
        if not v or len(v) < 1:
            raise ValueError("at_least_one_line")
        return v

class JournalEntryOut(BaseModel):
    id: UUID
    company_id: UUID
    number: Optional[int] = None
    fiscal_year: int
    period: str
    date: date
    description: Optional[str]
    total_debit: Money
    total_credit: Money
    status: str
    original_entry_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    created_at: Optional[str] = None
    posted_at: Optional[str] = None
    lines: List[JournalLineIn]
    attachments: Optional[List[str]] = []

class ValidationErrorResponse(BaseModel):
    code: str
    message: Dict[str, str]

class SimpleResponse(BaseModel):
    code: str
    message: Dict[str, str]
