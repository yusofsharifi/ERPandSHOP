from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from fastapi.responses import FileResponse
from typing import Optional
from app.api.deps import get_db, get_locale, role_required, get_current_user
from app.services.reports_service import reports_service
from app.schemas import reports as reports_schemas
from app.core.config import settings
from app.tasks.reports_tasks import export_report, refresh_materialized
from app.celery_app import celery_app
from app.db.session import get_engine
from sqlalchemy.orm import Session
import os, json
from app.utils.drill_token import generate_drill_token, verify_drill_token

router = APIRouter(prefix='/reports')


@router.get('/trial-balance', response_model=dict)
def trial_balance(company_id: str = Query(...), as_of_date: str = Query(...), include_zero_balance: bool = Query(False), currency: Optional[str] = Query(None), db: Session = Depends(get_db), locale: str = Depends(get_locale)):
    try:
        res = reports_service.trial_balance(db, company_id, as_of_date, include_zero_balance, currency)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail={ 'fa': 'خطا در تولید گزارش', 'en': 'Failed to generate report', 'error': str(e) })


@router.get('/balance-sheet', response_model=list)
def balance_sheet(company_id: str = Query(...), as_of_date: str = Query(...), db: Session = Depends(get_db)):
    try:
        res = reports_service.balance_sheet(db, company_id, as_of_date)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail={'fa':'خطا','en':'Failed','error':str(e)})


@router.get('/pnl', response_model=list)
def pnl(company_id: str = Query(...), date_from: str = Query(...), date_to: str = Query(...), include_cogs: bool = Query(False), db: Session = Depends(get_db)):
    try:
        res = reports_service.pnl(db, company_id, date_from, date_to)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail={'fa':'خطا','en':'Failed','error':str(e)})


@router.get('/cashflow', response_model=list)
def cashflow(company_id: str = Query(...), date_from: str = Query(...), date_to: str = Query(...), method: str = Query('direct'), db: Session = Depends(get_db)):
    try:
        res = reports_service.cashflow(db, company_id, date_from, date_to, method)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail={'fa':'خطا','en':'Failed','error':str(e)})


@router.get('/ledger', response_model=dict)
def ledger(company_id: str = Query(...), account_id: str = Query(...), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None), page: int = Query(1), per_page: int = Query(100)):
    try:
        res = reports_service.account_ledger(get_db().__next__(), company_id, account_id, date_from, date_to, page, per_page)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail={'fa':'خطا','en':'Failed','error':str(e)})


@router.post('/export')
def export(report_type: str = Query(...), request: Request = None, background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user=Depends(role_required('finance_view'))):
    # enqueue export job
    params = dict(request.query_params)
    res = export_report.delay(report_type, params)
    return {'job_id': res.id}


@router.get('/export/status/{job_id}')
def export_status(job_id: str):
    r = celery_app.AsyncResult(job_id)
    return {'id': job_id, 'status': r.status, 'result': r.result}


@router.post('/refresh-materialized', dependencies=[Depends(role_required('Admin'))])
def refresh_materialized_view(name: Optional[str] = None, company_id: Optional[str] = None, force: bool = False):
    # trigger background refresh via celery
    task = refresh_materialized.delay(name, company_id)
    return {'task_id': task.id}


# health
@router.get('/_health')
def health():
    return {'ok': True}
