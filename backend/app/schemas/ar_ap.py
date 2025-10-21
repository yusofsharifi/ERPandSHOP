from pydantic import BaseModel, Field, condecimal, EmailStr
from typing import List, Optional
from uuid import UUID
from datetime import date

Money = condecimal(max_digits=20, decimal_places=2)

class PartnerBase(BaseModel):
    name: str
    partner_type: str
    tax_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    credit_limit: Optional[Money] = None
    is_active: Optional[bool] = True

class PartnerCreate(PartnerBase):
    pass

class PartnerRead(PartnerBase):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

class InvoiceLineIn(BaseModel):
    product_id: Optional[UUID] = None
    description: Optional[str] = None
    qty: condecimal(max_digits=18, decimal_places=4) = 1
    unit_price: condecimal(max_digits=18, decimal_places=4) = 0
    tax_rate: condecimal(max_digits=5, decimal_places=4) = 0

class InvoiceLineRead(InvoiceLineIn):
    id: int
    line_total: Money

class InvoiceCreate(BaseModel):
    partner_id: UUID
    invoice_type: str
    date: date
    due_date: Optional[date] = None
    currency: Optional[str] = 'USD'
    lines: List[InvoiceLineIn]

class InvoiceRead(BaseModel):
    id: UUID
    partner_id: UUID
    invoice_no: str
    date: date
    due_date: Optional[date]
    total_amount: Money
    balance_amount: Money
    currency: str
    status: str
    invoice_type: str
    lines: List[InvoiceLineRead]

class InvoiceUpdate(BaseModel):
    date: Optional[date]
    due_date: Optional[date]
    currency: Optional[str]
    lines: Optional[List[InvoiceLineIn]]

class PaymentCreate(BaseModel):
    invoice_id: Optional[UUID] = None
    partner_id: UUID
    amount: Money
    method: str
    payment_date: date
    reference: Optional[str] = None

class PaymentRead(BaseModel):
    id: int
    invoice_id: Optional[UUID]
    partner_id: UUID
    amount: Money
    method: str
    payment_date: date
    reference: Optional[str]

class SimpleResponse(BaseModel):
    code: str
    message: dict
