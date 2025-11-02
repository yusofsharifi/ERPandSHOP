from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import date

class TrialBalanceAccount(BaseModel):
    account_code: str
    account_name: str
    opening_balance: float
    period_debit: float
    period_credit: float
    closing_balance: float

class TrialBalanceResponse(BaseModel):
    as_of_date: date
    period_start: date
    period_end: date
    accounts: List[TrialBalanceAccount]
    totals: Dict[str, float]

class LedgerRow(BaseModel):
    line_id: UUID
    journal_id: UUID
    journal_date: date
    journal_number: Optional[str]
    account_id: UUID
    account_code: str
    description: Optional[str]
    debit: float
    credit: float
    currency: Optional[str]
    exchange_rate: Optional[float]
    balance_running_line_currency: Optional[float]
    balance_running_company_currency: Optional[float]

class LedgerResponse(BaseModel):
    rows: List[LedgerRow]
    page: int
    per_page: int
    returned: int

class PnLRow(BaseModel):
    period_date: date
    revenue: float
    expenses: float
    cogs: float
    net_operating: float

class CashflowRow(BaseModel):
    period_date: date
    cash_inflows: float
    cash_outflows: float
    operating_cash_flow: float

class SimpleResponse(BaseModel):
    code: str
    message: Dict[str, str]
