from fastapi import APIRouter, Depends, HTTPException
from typing import List
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

@router.post('/runs', response_model=payroll_schemas.PayrollRunRead)
def create_run(payload: payroll_schemas.PayrollRunCreate, db: Session = Depends(get_db)):
    pr = payroll_service.create_run(db, payload.period_start, payload.period_end)
    return { 'id': pr.id, 'period_start': pr.period_start, 'period_end': pr.period_end, 'generated_at': pr.generated_at, 'status': pr.status }

@router.post('/runs/{run_id}/compute', response_model=payroll_schemas.PayrollComputeResponse)
def compute_run(run_id: UUID, payload: payroll_schemas.PayrollRunCreate = None, db: Session = Depends(get_db)):
    try:
        emp_ids = payload.employee_ids if payload else None
        res = payroll_service.compute_run(db, run_id, employee_ids=emp_ids)
        return { 'payroll_id': res['payroll_id'], 'lines_generated': res['lines_generated'] }
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'payroll_run_not_found','message':{'fa':'اجرای حقوق یافت نشد','en':'Payroll run not found'}})
    except ValueError as e:
        if str(e) == 'cannot_compute_non_draft':
            raise HTTPException(status_code=409, detail={'code':'cannot_compute_non_draft','message':{'fa':'قابل محاسبه نیست','en':'Cannot compute non-draft payroll'}})
        raise HTTPException(status_code=400, detail={'code':'validation_error','message':{'fa':str(e),'en':str(e)}})

@router.get('/runs')
def list_runs(db: Session = Depends(get_db)):
    items = payroll_service.list_runs(db)
    return [ { 'id': r.id, 'period_start': r.period_start, 'period_end': r.period_end, 'generated_at': r.generated_at, 'status': r.status } for r in items ]

@router.get('/runs/{run_id}/lines', response_model=List[payroll_schemas.PayrollLineRead])
def list_lines(run_id: UUID, db: Session = Depends(get_db)):
    lines = payroll_service.list_lines(db, run_id)
    return [ { 'id': l.id, 'payroll_id': l.payroll_id, 'employee_id': l.employee_id, 'period_start': l.period_start, 'period_end': l.period_end, 'gross': l.gross, 'taxes': l.taxes, 'deductions': l.deductions, 'net': l.net, 'components': l.components } for l in lines ]

@router.post('/runs/{run_id}/post')
def post_run(run_id: UUID, db: Session = Depends(get_db)):
    try:
        res = payroll_service.post_run(db, run_id)
        return { 'code': 'ok', 'message': {'fa':'پست انجام شد','en':'Payroll posted'}, 'journal_entry_id': res.get('journal_entry_id') }
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'payroll_run_not_found','message':{'fa':'اجرای حقوق یافت نشد','en':'Payroll run not found'}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'code':'validation_error','message':{'fa':str(e),'en':str(e)}})
