from fastapi import APIRouter, Depends, HTTPException
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from typing import List
from app.models.payroll import Employee
from pydantic import BaseModel

router = APIRouter()

class EmployeeCreate(BaseModel):
    name: str
    national_id: str = None
    employment_no: str = None
    bank_account: str = None
    hire_date: str = None
    department_id: str = None
    tax_code: str = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/employees')
def list_employees(db: Session = Depends(get_db)):
    items = db.query(Employee).order_by(Employee.name).all()
    return [ { 'id': str(e.id), 'name': e.name, 'national_id': e.national_id, 'employment_no': e.employment_no, 'bank_account': e.bank_account } for e in items ]


@router.post('/employees', status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    e = Employee(name=payload.name, national_id=payload.national_id, employment_no=payload.employment_no, bank_account=payload.bank_account, tax_code=payload.tax_code)
    db.add(e)
    db.commit()
    db.refresh(e)
    return { 'id': str(e.id), 'name': e.name, 'national_id': e.national_id, 'employment_no': e.employment_no }
