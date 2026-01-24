from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CustomerContactCreate(BaseModel):
    contact_name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class CustomerContactRead(CustomerContactCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class CustomerNoteCreate(BaseModel):
    note: str


class CustomerNoteRead(BaseModel):
    id: UUID
    note: str
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        orm_mode = True


class CustomerTransactionCreate(BaseModel):
    amount: float
    transaction_type: str
    reference_id: Optional[UUID] = None
    date: Optional[datetime] = None


class CustomerTransactionRead(CustomerTransactionCreate):
    id: UUID

    class Config:
        orm_mode = True


class CustomerCreate(BaseModel):
    company_id: UUID
    name: str
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    national_id: Optional[str] = None
    registration_no: Optional[str] = None
    credit_limit: Optional[float] = 0
    contacts: Optional[List[CustomerContactCreate]] = []


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    national_id: Optional[str] = None
    registration_no: Optional[str] = None
    credit_limit: Optional[float] = None
    status: Optional[str] = None


class CustomerRead(BaseModel):
    id: UUID
    partner_id: UUID
    company_id: UUID
    customer_no: str
    name: str
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    national_id: Optional[str] = None
    registration_no: Optional[str] = None
    credit_limit: float
    status: str
    contacts: List[CustomerContactRead] = []
    notes: List[CustomerNoteRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
