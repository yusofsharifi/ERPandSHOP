from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from uuid import UUID


class AccountBase(BaseModel):
    company_id: UUID
    name: str
    currency: str = 'USD'
    is_active: bool = True

class CashAccountCreate(AccountBase):
    code: str

class BankAccountCreate(AccountBase):
    bank_name: str
    account_number: str
    iban: Optional[str] = None
    routing_code: Optional[str] = None

class CashAccountRead(BaseModel):
    id: UUID
    company_id: UUID
    code: Optional[str]
    name: str
    currency: str
    balance: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BankAccountRead(BaseModel):
    id: UUID
    company_id: UUID
    bank_name: str
    account_number: str
    iban: Optional[str]
    currency: str
    balance: float
    routing_code: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TransferCreate(BaseModel):
    from_type: str = Field(..., description="cash|bank|other")
    from_id: Optional[UUID]
    to_type: str = Field(..., description="cash|bank|other")
    to_id: Optional[UUID]
    amount: float
    currency: str = 'USD'
    exchange_rate: Optional[float] = 1.0
    date: Optional[datetime] = None
    reference: Optional[str] = None
    allow_overdraft: Optional[bool] = False

class TreasuryTransactionRead(BaseModel):
    id: UUID
    company_id: UUID
    source_type: str
    source_id: Optional[UUID]
    target_type: str
    target_id: Optional[UUID]
    amount: float
    currency: str
    exchange_rate: float
    date: datetime
    reference: Optional[str]
    posted: bool
    journal_entry_id: Optional[UUID]
    created_at: datetime

    class Config:
        orm_mode = True

class ReconciliationUploadResult(BaseModel):
    reconciliation_id: UUID
    imported_lines: int
    message: Optional[str]

class MatchSuggestion(BaseModel):
    line_id: UUID
    txn_id: Optional[UUID]
    score: float
    reason: Optional[str]

class ReconciliationRead(BaseModel):
    id: UUID
    company_id: UUID
    bank_account_id: UUID
    period_start: date
    period_end: date
    status: str
    reconciliation_data: Optional[Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
