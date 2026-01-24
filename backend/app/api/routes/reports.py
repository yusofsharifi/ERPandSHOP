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
def ledger(company_id: str = Query(None), account_id: str = Query(None), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None), page: int = Query(1), per_page: int = Query(100), drill_token: Optional[str] = Query(None)):
    try:
        # If a drill_token provided, validate and extract params
        if drill_token:
            payload = verify_drill_token(drill_token)
            if not payload:
                raise HTTPException(status_code=400, detail={'fa':'توکن نامعتبر','en':'Invalid drill token'})
            company_id = payload.get('company_id') or company_id
            account_id = payload.get('account_id') or account_id
            date_from = payload.get('date_from') or date_from
            date_to = payload.get('date_to') or date_to
        if not company_id or not account_id:
            raise HTTPException(status_code=400, detail={'fa':'پارامترها ناقص','en':'Missing parameters'})
        res = reports_service.account_ledger(get_db().__next__(), company_id, account_id, date_from, date_to, page, per_page)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={'fa':'خطا','en':'Failed','error':str(e)})


@router.post('/drill-token')
def create_drill_token(company_id: str = Query(...), account_id: str = Query(...), date_from: Optional[str] = Query(None), date_to: Optional[str] = Query(None), ttl: int = Query(300), current_user=Depends(role_required('finance_view'))):
    payload = {'company_id': company_id, 'account_id': account_id, 'date_from': date_from, 'date_to': date_to, 'requested_by': getattr(current_user,'id',None)}
    token = generate_drill_token(payload, expires_seconds=ttl)
    return {'drill_token': token, 'expires_in': ttl}


@router.post('/export')
def export(report_type: str = Query(...), request: Request = None, background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user=Depends(role_required('finance_view'))):
    # enqueue export job
    params = dict(request.query_params)
    res = export_report.delay(report_type, params)
    # write request meta mapping to validate downloads
    out_dir = os.path.join('uploads','exports')
    os.makedirs(out_dir, exist_ok=True)
    meta = {'job_id': res.id, 'requested_by': getattr(current_user,'id',None), 'report_type': report_type, 'params': params}
    try:
        with open(os.path.join(out_dir, f"{res.id}.request.json"), 'w') as mf:
            json.dump(meta, mf)
    except Exception:
        pass
    return {'job_id': res.id}


@router.get('/export/status/{job_id}')
def export_status(job_id: str):
    r = celery_app.AsyncResult(job_id)
    return {'id': job_id, 'status': r.status, 'result': r.result}


@router.get('/export/download/{job_id}')
def export_download(job_id: str, current_user = Depends(get_current_user)):
    out_dir = os.path.join('uploads','exports')
    req_meta_path = os.path.join(out_dir, f"{job_id}.request.json")
    # check requester
    try:
        if os.path.exists(req_meta_path):
            with open(req_meta_path, 'r') as mf:
                meta = json.load(mf)
            owner = meta.get('requested_by')
            # allow Admin or owner
            if getattr(current_user,'role',None) and getattr(current_user.role,'name',None) == 'Admin':
                allowed = True
            else:
                allowed = (str(owner) == str(getattr(current_user,'id',None)))
            if not allowed:
                raise HTTPException(status_code=403, detail={'fa':'دسترسی ممنوع','en':'Forbidden'})
    except HTTPException:
        raise
    except Exception:
        # if no meta, deny download for safety
        raise HTTPException(status_code=404, detail={'fa':'فایل یافت نشد','en':'Not found'})
    # get task result
    r = celery_app.AsyncResult(job_id)
    res = r.result
    if not res or not isinstance(res, dict) or not res.get('path'):
        raise HTTPException(status_code=404, detail={'fa':'خروجی هنوز آماده نیست','en':'Export not ready'})
    path = res.get('path')
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail={'fa':'فایل یافت نشد','en':'Not found'})
    return FileResponse(path, filename=os.path.basename(path))


@router.post('/refresh-materialized', dependencies=[Depends(role_required('Admin'))])
def refresh_materialized_view(name: Optional[str] = None, company_id: Optional[str] = None, force: bool = False):
    # trigger background refresh via celery
    task = refresh_materialized.delay(name, company_id)
    return {'task_id': task.id}


# health
@router.get('/_health')
def health():
    return {'ok': True}
