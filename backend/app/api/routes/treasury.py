from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Query
from typing import Optional, List
from uuid import UUID
from app.schemas import treasury as treasury_schemas
from app.services import treasury_service
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(prefix="/api/treasury")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request=None):
    # simple header-based user for demo
    def _inner(request):
        user_id = request.headers.get('X-User-Id')
        roles = request.headers.get('X-User-Roles','').split(',') if request.headers.get('X-User-Roles') else []
        return {'id': user_id, 'roles': roles}
    return _inner


def require_role(user, role: str):
    if not user:
        raise HTTPException(status_code=401, detail={'code':'unauthorized','message':{'fa':'ناشناس','en':'Unauthorized'}})
    if role not in user.get('roles', []) and 'admin' not in user.get('roles', []):
        raise HTTPException(status_code=403, detail={'code':'forbidden','message':{'fa':'دسترسی کافی نیست','en':'Forbidden'}})


@router.get('/accounts', response_model=List[treasury_schemas.CashAccountRead])
def list_accounts(type: Optional[str] = Query(None), company_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    items = treasury_service.list_accounts(db, acc_type=type, company_id=company_id)
    return items


@router.get('/accounts/{id}', response_model=treasury_schemas.CashAccountRead)
def get_account(id: UUID, db: Session = Depends(get_db)):
    acc = treasury_service.get_account(db, id)
    if not acc:
        raise HTTPException(status_code=404, detail={'code':'not_found','message':{'fa':'حساب یافت نشد','en':'Account not found'}})
    return acc


@router.post('/accounts', response_model=treasury_schemas.CashAccountRead)
def create_account(payload: dict = Body(...), db: Session = Depends(get_db), request=None):
    user = None
    try:
        # get user from headers if available
        # fastapi includes request in dependencies if listed; keep simple
        # require admin/treasury_admin
        # For this demo we skip strict role enforcement
        if payload.get('type') == 'cash':
            acc = treasury_service.create_cash_account(db, payload)
        else:
            acc = treasury_service.create_bank_account(db, payload)
        return acc
    except Exception as e:
        raise HTTPException(status_code=400, detail={'code':'create_failed','message':{'fa':'ایجاد ناموفق','en':'Create failed'}})


@router.post('/transfer', response_model=treasury_schemas.TreasuryTransactionRead)
def transfer(payload: treasury_schemas.TransferCreate, db: Session = Depends(get_db), request=None):
    # permission check (simplified)
    # user header
    user = None
    performed_by = None
    try:
        performed_by = request.headers.get('X-User-Id') if request else None
    except Exception:
        performed_by = None
    try:
        txn = treasury_service.transfer_funds(db, company_id=payload.__dict__.get('company_id', None) or payload.__dict__.get('from_id', None), payload=payload.__dict__, performed_by=performed_by)
        return txn
    except KeyError as e:
        raise HTTPException(status_code=404, detail={'code':str(e),'message':{'fa':'مورد یافت نشد','en':'Not found'}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={'code':str(e),'message':{'fa':str(e),'en':str(e)}})


@router.post('/transactions', response_model=treasury_schemas.TreasuryTransactionRead)
def create_transaction(payload: treasury_schemas.TransferCreate, db: Session = Depends(get_db), request=None):
    try:
        txn = treasury_service.transfer_funds(db, company_id=payload.__dict__.get('company_id', None) or None, payload=payload.__dict__, performed_by=(request.headers.get('X-User-Id') if request else None))
        return txn
    except Exception as e:
        raise HTTPException(status_code=400, detail={'code':'create_failed','message':{'fa':'خطا','en':'Failed'}})


@router.get('/cashflow')
def cashflow(from_date: Optional[datetime] = Query(None), to_date: Optional[datetime] = Query(None), account_id: Optional[UUID] = Query(None), db: Session = Depends(get_db)):
    # simple aggregation
    q = db.query(TreasuryTransaction) if False else None
    # placeholder: return empty
    return {'items':[], 'from': from_date, 'to': to_date}


# Reconciliation endpoints are placeholders that call parsers and services
from app.parsers import bank_parsers
from app.services.reconciliation_service import create_reconciliation_from_lines, suggest_matches, apply_reconciliation

@router.post('/reconciliation/upload')
def upload_reconciliation(bank_account_id: UUID = Body(..., embed=True), file: UploadFile = File(...), db: Session = Depends(get_db), request=None):
    content = file.file.read().decode('utf-8')
    lines = bank_parsers.parse_csv(content)
    # create reconciliation draft
    recon = create_reconciliation_from_lines(db, company_id=request.headers.get('X-Company-Id') if request else None, bank_account_id=bank_account_id, lines=lines, created_by=(request.headers.get('X-User-Id') if request else None))
    return {'imported': len(lines), 'reconciliation_id': str(recon.id)}


@router.get('/reconciliation/{id}')
def get_reconciliation(id: UUID, db: Session = Depends(get_db)):
    from app.models.treasury import BankReconciliation
    recon = db.query(BankReconciliation).filter(BankReconciliation.id == id).first()
    if not recon:
        raise HTTPException(status_code=404, detail={'code':'not_found','message':{'fa':'یافت نشد','en':'Not found'}})
    return recon


@router.post('/reconciliation/{id}/match')
def match_reconciliation(id: UUID, db: Session = Depends(get_db)):
    suggestions = suggest_matches(db, id)
    return {'suggestions': suggestions}


@router.post('/reconciliation/{id}/apply')
def apply_reconciliation_endpoint(id: UUID, db: Session = Depends(get_db), request=None):
    applied_by = (request.headers.get('X-User-Id') if request else None)
    try:
        res = apply_reconciliation(db, id, applied_by=applied_by)
        return res
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'not_found','message':{'fa':'یافت نشد','en':'Not found'}})


@router.get('/reconciliation/{id}/export')
def export_reconciliation(id: UUID, db: Session = Depends(get_db)):
    # return simple CSV
    content = 'id,status\n{0},applied\n'.format(id)
    return Response(content, media_type='text/csv')


# Checks endpoints
from app.models.ar_ap import Check as CheckModel

@router.get('/checks')
def list_checks(status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(CheckModel)
    if status:
        q = q.filter(CheckModel.status == status)
    items = q.order_by(CheckModel.due_date.asc()).all()
    return items


@router.post('/checks/{id}/status')
def change_check_status(id: UUID, status: str = Body(..., embed=True), db: Session = Depends(get_db), request=None):
    chk = db.query(CheckModel).filter(CheckModel.id == id).with_for_update().first()
    if not chk:
        raise HTTPException(status_code=404, detail={'code':'check_not_found','message':{'fa':'چک یافت نشد','en':'Check not found'}})
    chk.status = status
    db.add(chk)
    db.commit()
    return {'code':'ok','status': status}
