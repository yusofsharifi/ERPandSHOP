from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional
from uuid import UUID
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.schemas import payroll as payroll_schemas
from app.services.payroll_service import payroll_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/employees', response_model=List[payroll_schemas.EmployeeRead])
def list_employees(db: Session = Depends(get_db)):
    items = payroll_service.list_employees(db)
    return [
        {
            'id': i.id,
            'company_id': i.company_id,
            'employee_code': i.employee_code,
            'first_name': i.first_name,
            'last_name': i.last_name,
            'national_id': i.national_id,
            'job_title': i.job_title,
            'department_id': i.department_id,
            'hire_date': i.hire_date,
            'contract_type': str(i.contract_type) if getattr(i,'contract_type',None) else None,
            'base_salary': i.base_salary,
            'bank_account': i.bank_account,
            'iban': i.iban,
            'is_active': i.is_active,
        }
        for i in items
    ]


@router.post('/structure', response_model=payroll_schemas.SalaryStructureRead, status_code=201)
def create_structure(payload: payroll_schemas.SalaryStructureCreate, db: Session = Depends(get_db)):
    s = payroll_service.create_or_update_structure(db, payload)
    return {
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'currency': s.currency,
        'rules': s.rules,
        'is_default': s.is_default,
        'created_at': s.created_at,
    }


@router.put('/structure/{structure_id}', response_model=payroll_schemas.SalaryStructureRead)
def update_structure(structure_id: UUID, payload: payroll_schemas.SalaryStructureCreate, db: Session = Depends(get_db)):
    try:
        s = payroll_service.create_or_update_structure(db, payload, struct_id=structure_id)
        return {
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'currency': s.currency,
            'rules': s.rules,
            'is_default': s.is_default,
            'created_at': s.created_at,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'structure_not_found','message':{'fa':'ساختار حقوق یافت نشد','en':'Salary structure not found'}})


@router.get('/periods', response_model=List[payroll_schemas.PayrollPeriodRead])
def list_periods(db: Session = Depends(get_db)):
    items = payroll_service.list_periods(db)
    return [
        {
            'id': p.id,
            'company_id': p.company_id,
            'name': p.name,
            'start_date': p.start_date,
            'end_date': p.end_date,
            'status': str(p.status),
            'created_by': p.created_by,
            'created_at': p.created_at,
        }
        for p in items
    ]


@router.post('/periods', response_model=payroll_schemas.PayrollPeriodRead, status_code=201)
def create_period(payload: payroll_schemas.PayrollPeriodCreate, db: Session = Depends(get_db)):
    p = payroll_service.create_period(db, payload)
    return {
        'id': p.id,
        'company_id': p.company_id,
        'name': p.name,
        'start_date': p.start_date,
        'end_date': p.end_date,
        'status': str(p.status),
        'created_by': p.created_by,
        'created_at': p.created_at,
    }


@router.post('/periods/{period_id}/generate')
def generate_period(period_id: UUID, db: Session = Depends(get_db)):
    try:
        res = payroll_service.generate_for_period(db, period_id)
        return {'code':'ok','message':{'fa':'تولید شد','en':'Generated'}, 'generated': res.get('generated'), 'payrolls_created': res.get('payrolls_created')}
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'period_not_found','message':{'fa':'دوره یافت نشد','en':'Period not found'}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'code':str(e),'message':{'fa':str(e),'en':str(e)}})


@router.get('/{payroll_id}')
def payroll_detail(payroll_id: UUID, db: Session = Depends(get_db)):
    try:
        res = payroll_service.get_payroll_detail(db, payroll_id)
        p = res['payroll']
        return {
            'payroll': {
                'id': p.id,
                'employee_id': p.employee_id,
                'period_id': p.period_id,
                'structure_id': p.structure_id,
                'gross_salary': p.gross_salary,
                'total_deductions': p.total_deductions,
                'net_salary': p.net_salary,
                'payment_status': str(p.payment_status),
                'pay_date': p.pay_date,
                'created_at': p.created_at,
            },
            'lines': [
                { 'id': l.id, 'code': l.code, 'name': l.name, 'type': str(l.type), 'amount': l.amount, 'formula': l.formula } for l in res['lines']
            ],
            'deductions': [ { 'id': d.id, 'type': d.type, 'amount': d.amount, 'description': d.description } for d in res['deductions'] ],
            'bonuses': [ { 'id': b.id, 'type': b.type, 'amount': b.amount, 'description': b.description } for b in res['bonuses'] ],
        }
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'payroll_not_found','message':{'fa':'حقوق یافت نشد','en':'Payroll not found'}})


@router.post('/{payroll_id}/validate')
def validate_payroll(payroll_id: UUID, db: Session = Depends(get_db)):
    try:
        res = payroll_service.validate_payroll(db, payroll_id)
        return {'code':'ok','message':{'fa':'تایید شد','en':'Validated'}, 'journal_entry_id': res.get('journal_entry_id')}
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'payroll_not_found','message':{'fa':'حقوق یافت نشد','en':'Payroll not found'}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'code':str(e),'message':{'fa':str(e),'en':str(e)}})


@router.post('/{payroll_id}/pay')
def pay_payroll(payroll_id: UUID, pay_date: Optional[date] = Body(None), db: Session = Depends(get_db)):
    try:
        res = payroll_service.pay_payroll(db, payroll_id, pay_date=pay_date)
        return {'code':'ok','message':{'fa':'پرداخت شد','en':'Paid'}, 'journal_entry_id': res.get('journal_entry_id')}
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'payroll_not_found','message':{'fa':'حقوق یافت نشد','en':'Payroll not found'}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'code':str(e),'message':{'fa':str(e),'en':str(e)}})


@router.get('/report')
def payroll_report(company_id: Optional[UUID] = Query(None), period_id: Optional[UUID] = Query(None), department_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    query = payroll_schemas.PayrollReportQuery(company_id=company_id, period_id=period_id, department_id=department_id)
    res = payroll_service.payroll_report(db, query)
    return {
        'rows': [ { 'key': r['key'], 'gross': r['gross'], 'deductions': r['deductions'], 'net': r['net'] } for r in res['rows'] ],
        'total_gross': res['total_gross'],
        'total_deductions': res['total_deductions'],
        'total_net': res['total_net'],
    }
