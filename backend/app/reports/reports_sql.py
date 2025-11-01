from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session


def fn_trial_balance(db: Session, company_id: str, as_of_date: str) -> Dict[str, Any]:
    q = text("SELECT fn_trial_balance(:company_id::uuid, :as_of_date::date) as result")
    r = db.execute(q, {'company_id': company_id, 'as_of_date': as_of_date}).fetchone()
    return r['result'] if r else {}


def fn_account_ledger(db: Session, company_id: str, account_id: str, date_from: Optional[str]=None, date_to: Optional[str]=None, page:int=1, per_page:int=100) -> List[Dict[str, Any]]:
    q = text("SELECT * FROM fn_account_ledger(:company_id::uuid, :account_id::uuid, :date_from::date, :date_to::date, :page::int, :per_page::int)")
    rows = db.execute(q, {'company_id': company_id, 'account_id': account_id, 'date_from': date_from, 'date_to': date_to, 'page': page, 'per_page': per_page}).fetchall()
    return [dict(row) for row in rows]


def fn_balance_sheet(db: Session, company_id: str, as_of_date: str) -> List[Dict[str, Any]]:
    q = text("SELECT * FROM fn_balance_sheet(:company_id::uuid, :as_of_date::date)")
    rows = db.execute(q, {'company_id': company_id, 'as_of_date': as_of_date}).fetchall()
    return [dict(r) for r in rows]


def fn_pnl(db: Session, company_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
    q = text("SELECT * FROM fn_pnl(:company_id::uuid, :date_from::date, :date_to::date)")
    rows = db.execute(q, {'company_id': company_id, 'date_from': date_from, 'date_to': date_to}).fetchall()
    return [dict(r) for r in rows]


def fn_cashflow(db: Session, company_id: str, date_from: str, date_to: str, method: str='direct') -> List[Dict[str, Any]]:
    q = text("SELECT * FROM fn_cashflow(:company_id::uuid, :date_from::date, :date_to::date, :method::text)")
    rows = db.execute(q, {'company_id': company_id, 'date_from': date_from, 'date_to': date_to, 'method': method}).fetchall()
    return [dict(r) for r in rows]
