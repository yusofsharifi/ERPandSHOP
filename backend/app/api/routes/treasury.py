from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.schemas import treasury as tr_schemas
from app.services.treasury_service import treasury_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/cash_accounts')
def list_cash_accounts(db: Session = Depends(get_db)):
    items = treasury_service.list_cash_accounts(db)
    return { 'items': [ { 'id': str(i.id), 'name': i.name, 'code': i.code, 'balance': str(i.balance), 'currency': i.currency } for i in items ] }

@router.post('/cash_accounts', status_code=201)
def create_cash_account(payload: tr_schemas.CashAccountCreate, db: Session = Depends(get_db)):
    ca = treasury_service.create_cash_account(db, payload)
    return { 'id': str(ca.id), 'name': ca.name, 'code': ca.code, 'balance': str(ca.balance), 'currency': ca.currency }

@router.get('/bank_accounts')
def list_bank_accounts(db: Session = Depends(get_db)):
    items = treasury_service.list_bank_accounts(db)
    return { 'items': [ { 'id': str(i.id), 'bank_name': i.bank_name, 'account_number': i.account_number, 'balance': str(i.balance), 'currency': i.currency } for i in items ] }

@router.post('/bank_accounts', status_code=201)
def create_bank_account(payload: tr_schemas.BankAccountCreate, db: Session = Depends(get_db)):
    ba = treasury_service.create_bank_account(db, payload)
    return { 'id': str(ba.id), 'bank_name': ba.bank_name, 'account_number': ba.account_number, 'balance': str(ba.balance), 'currency': ba.currency }

@router.post('/transfer', status_code=201)
def transfer(payload: tr_schemas.TreasuryTransactionCreate, db: Session = Depends(get_db)):
    try:
        tx = treasury_service.transfer(db, payload)
        return { 'id': str(tx.id), 'source_type': tx.source_type, 'source_id': str(tx.source_id) if tx.source_id else None, 'target_type': tx.target_type, 'target_id': str(tx.target_id) if tx.target_id else None, 'amount': str(tx.amount), 'currency': tx.currency, 'date': str(tx.date) }
    except KeyError:
        raise HTTPException(status_code=404, detail={'code':'account_not_found','message':{'fa':'حساب یافت نشد','en':'Account not found'}})
    except ValueError as e:
        if str(e) == 'insufficient_funds':
            raise HTTPException(status_code=400, detail={'code':'insufficient_funds','message':{'fa':'موجودی کافی نیست','en':'Insufficient funds'}})
        raise HTTPException(status_code=400, detail={'code':'validation_error','message':{'fa':str(e),'en':str(e)}})

@router.get('/transactions')
def list_transactions(limit: int = 100, db: Session = Depends(get_db)):
    items = treasury_service.list_transactions(db, limit=limit)
    return { 'items': [ { 'id': str(i.id), 'source_type': i.source_type, 'source_id': str(i.source_id) if i.source_id else None, 'target_type': i.target_type, 'target_id': str(i.target_id) if i.target_id else None, 'amount': str(i.amount), 'currency': i.currency, 'date': str(i.date), 'reference': i.reference } for i in items ] }

@router.post('/bank_reconciliations', status_code=201)
def create_reconciliation(payload: tr_schemas.BankReconciliationCreate, db: Session = Depends(get_db)):
    rec = treasury_service.create_bank_reconciliation(db, payload)
    return { 'id': str(rec.id), 'bank_account_id': str(rec.bank_account_id), 'period_start': str(rec.period_start), 'period_end': str(rec.period_end), 'status': rec.status, 'reconciliation_data': rec.reconciliation_data }
