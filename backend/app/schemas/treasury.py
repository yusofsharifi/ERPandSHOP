from pydantic import BaseModel, condecimal
from typing import Optional, List
from uuid import UUID
from datetime import date

Money = condecimal(max_digits=20, decimal_places=2)

class CashAccountCreate(BaseModel):
    name: str
    code: Optional[str]
    currency: Optional[str] = 'USD'
    balance: Optional[Money] = 0

class CashAccountRead(CashAccountCreate):
    id: UUID

class BankAccountCreate(BaseModel):
    bank_name: str
    account_number: str
    currency: Optional[str] = 'USD'
    balance: Optional[Money] = 0

class BankAccountRead(BankAccountCreate):
    id: UUID

class TreasuryTransactionCreate(BaseModel):
    source_type: str
    source_id: Optional[UUID]
    target_type: str
    target_id: Optional[UUID]
    amount: Money
    currency: Optional[str] = 'USD'
    date: date
    reference: Optional[str]
    created_by: Optional[UUID]

class TreasuryTransactionRead(TreasuryTransactionCreate):
    id: UUID

class BankReconciliationCreate(BaseModel):
    bank_account_id: UUID
    period_start: date
    period_end: date
    reconciliation_data: Optional[dict]

class BankReconciliationRead(BankReconciliationCreate):
    id: UUID
    status: str
