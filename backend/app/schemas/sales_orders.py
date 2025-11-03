from pydantic import BaseModel, condecimal
from typing import List, Optional
from uuid import UUID
from datetime import date

Money = condecimal(max_digits=20, decimal_places=2)
Qty = condecimal(max_digits=18, decimal_places=4)

class SalesOrderLineIn(BaseModel):
    product_id: Optional[int] = None
    description: Optional[str] = None
    quantity: Qty = 1
    unit_price: condecimal(max_digits=18, decimal_places=4) = 0
    discount: Optional[Money] = 0
    tax_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = 0

class SalesOrderLineRead(SalesOrderLineIn):
    id: UUID
    line_total: Money

    class Config:
        orm_mode = True

class SalesOrderCreate(BaseModel):
    company_id: UUID
    customer_id: UUID
    date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    lines: List[SalesOrderLineIn]

class SalesOrderUpdate(BaseModel):
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None
    lines: Optional[List[SalesOrderLineIn]] = None

class SalesOrderRead(BaseModel):
    id: UUID
    order_no: Optional[str]
    company_id: UUID
    customer_id: UUID
    date: date
    expected_delivery_date: Optional[date]
    status: str
    total_amount: Money
    total_discount: Money
    total_tax: Money
    net_amount: Money
    notes: Optional[str]
    lines: List[SalesOrderLineRead] = []

    class Config:
        orm_mode = True

class SimpleResponse(BaseModel):
    code: str
    message: dict
