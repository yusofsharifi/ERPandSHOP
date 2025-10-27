from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db import session
from app.core.config import settings
from app.services.gl_service import gl_service
import hashlib
import json

# Caching: try Redis, otherwise in-memory TTL cache
_redis = None
_cache_store = {}

try:
    import redis
    if settings.REDIS_URL:
        _redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    else:
        _redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    _redis.ping()
except Exception:
    _redis = None


def _cache_get(key: str):
    ttl = settings.CACHE_TTL_SECONDS
    if _redis:
        try:
            v = _redis.get(key)
            if v is None:
                return None
            return json.loads(v)
        except Exception:
            return None
    # in-memory
    rec = _cache_store.get(key)
    if not rec:
        return None
    value, exp = rec
    if datetime.utcnow() > exp:
        del _cache_store[key]
        return None
    return value


def _cache_set(key: str, value, ttl: int = None):
    ttl = ttl or settings.CACHE_TTL_SECONDS
    if _redis:
        try:
            _redis.setex(key, int(ttl), json.dumps(value, default=str))
            return
        except Exception:
            pass
    _cache_store[key] = (value, datetime.utcnow() + timedelta(seconds=ttl))


def _exec_sql(sql: str, params: Dict[str, Any] = None, prefer_read: bool = True):
    params = params or {}
    try:
        eng = session.get_engine(prefer_read=prefer_read)
        with eng.connect() as conn:
            res = conn.execute(text(sql), params)
            cols = res.keys()
            rows = [dict(zip(cols, row)) for row in res.fetchall()]
            return rows
    except Exception:
        return None


def _cache_key(prefix: str, params: Dict[str, Any]):
    payload = json.dumps(params, sort_keys=True, default=str)
    h = hashlib.sha1(payload.encode('utf-8')).hexdigest()
    return f"reports:{prefix}:{h}"


def trial_balance_sql(company_id: str, date_to: Optional[str] = None, include_zero: bool = False):
    # Materialized view suggestion and query
    mv_sql = f"""
    -- Materialized view: mv_trial_balance
    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_trial_balance AS
    SELECT
      a.id as account_id,
      a.code as account_code,
      a.name as account_name,
      a.type as account_type,
      COALESCE(SUM(jl.debit),0) as total_debit,
      COALESCE(SUM(jl.credit),0) as total_credit,
      COALESCE(SUM(jl.debit) - SUM(jl.credit),0) as balance
    FROM accounts a
    LEFT JOIN journal_lines jl ON jl.account_id = a.id
    LEFT JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
    WHERE a.company_id = :company_id
    """
    if date_to:
        mv_sql += " AND je.date <= :date_to\n"
    mv_sql += "GROUP BY a.id, a.code, a.name, a.type;"

    query_sql = f"SELECT account_id, account_code, account_name, account_type, total_debit, total_credit, balance FROM mv_trial_balance WHERE 1=1"
    if not include_zero:
        query_sql += " AND (total_debit <> 0 OR total_credit <> 0)"
    if date_to:
        # In case materialized view not filtered by date, restrict by joining journal_entries — keep simple: rely on MV
        pass
    query_sql += " ORDER BY account_code"

    return mv_sql, query_sql


def trial_balance(company_id: str, date_to: Optional[str] = None, include_zero: bool = False):
    # Try SQL execution first
    mv_sql, query_sql = trial_balance_sql(company_id, date_to=date_to, include_zero=include_zero)
    rows = _exec_sql(query_sql, {"company_id": company_id, "date_to": date_to})
    if rows is not None:
        return rows

    # Fallback to in-memory aggregation
    items = gl_service.trial_balance(company_id, date_to=date_to)
    if not include_zero:
        items = [i for i in items if (i.get('debit',0) != 0 or i.get('credit',0) != 0)]
    return items


def balance_sheet(company_id: str, date_to: Optional[str] = None):
    # Balance sheet groups by account type
    sql = f"""
    SELECT account_type,
      SUM(total_debit) as total_debit,
      SUM(total_credit) as total_credit,
      SUM(total_debit - total_credit) as net_balance
    FROM (
      SELECT a.type as account_type, COALESCE(SUM(jl.debit),0) as total_debit, COALESCE(SUM(jl.credit),0) as total_credit
      FROM accounts a
      LEFT JOIN journal_lines jl ON jl.account_id = a.id
      LEFT JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
      WHERE a.company_id = :company_id
    """
    if date_to:
        sql += " AND je.date <= :date_to\n"
    sql += " GROUP BY a.id, a.type) t GROUP BY account_type ORDER BY account_type"

    rows = _exec_sql(sql, {"company_id": company_id, "date_to": date_to})
    if rows is not None:
        return rows

    # Fallback: compute from trial_balance
    tb = trial_balance(company_id, date_to=date_to, include_zero=True)
    groups = {}
    for r in tb:
        acc_type = r.get('account_type') or 'unknown'
        debit = float(r.get('debit',0))
        credit = float(r.get('credit',0))
        grp = groups.setdefault(acc_type, {'total_debit':0.0,'total_credit':0.0})
        grp['total_debit'] += debit
        grp['total_credit'] += credit
    out = []
    for k,v in groups.items():
        out.append({'account_type': k, 'total_debit': v['total_debit'], 'total_credit': v['total_credit'], 'net_balance': v['total_debit']-v['total_credit']})
    return out


def pnl(company_id: str, date_from: Optional[str], date_to: Optional[str]):
    # Profit & Loss by account type (revenue/expense)
    sql = f"""
    SELECT a.code as account_code, a.name as account_name, SUM(jl.debit) as total_debit, SUM(jl.credit) as total_credit,
      SUM(jl.credit) - SUM(jl.debit) as net
    FROM accounts a
    JOIN journal_lines jl ON jl.account_id = a.id
    JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
    WHERE a.company_id = :company_id AND a.type IN ('revenue','expense')
    """
    if date_from:
        sql += " AND je.date >= :date_from\n"
    if date_to:
        sql += " AND je.date <= :date_to\n"
    sql += " GROUP BY a.id ORDER BY a.code"

    rows = _exec_sql(sql, {"company_id": company_id, "date_from": date_from, "date_to": date_to})
    if rows is not None:
        return rows

    # Fallback in-memory
    items = []
    # traverse entries
    for e in gl_service.list_entries({'company_id': company_id, 'date_from': date_from, 'date_to': date_to}, page=1, per_page=100000).get('items', []):
        for ln in e.get('lines',[]):
            # find account
            acc_id = str(ln.get('account_id'))
            # account metadata not present in in-memory service, skip grouping
            items.append({'account_id': acc_id, 'debit': ln.get('debit',0), 'credit': ln.get('credit',0)})
    return items


def cashflow(company_id: str, date_from: Optional[str], date_to: Optional[str], method: str = 'direct'):
    # For direct cash flow, classify cash accounts and sum inflows/outflows
    if method not in ('direct','indirect'):
        method = 'direct'
    sql = ''
    if method == 'direct':
        sql = f"""
        SELECT a.code as account_code, a.name as account_name,
          SUM(jl.debit) as total_debits, SUM(jl.credit) as total_credits
        FROM accounts a
        JOIN journal_lines jl ON jl.account_id = a.id
        JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
        WHERE a.company_id = :company_id AND a.type = 'asset' -- assume cash accounts flagged as asset (refine by account code or tag)
        """
        if date_from:
            sql += " AND je.date >= :date_from\n"
        if date_to:
            sql += " AND je.date <= :date_to\n"
        sql += " GROUP BY a.id ORDER BY a.code"
    else:
        # Indirect method: start with net income and adjust
        sql = f"""
        -- Simplified indirect cashflow: net income (revenues - expenses) plus adjustments (depreciation etc.)
        SELECT 'net_income' as line, SUM(COALESCE(jl.credit,0) - COALESCE(jl.debit,0)) as amount
        FROM accounts a
        JOIN journal_lines jl ON jl.account_id = a.id
        JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
        WHERE a.company_id = :company_id AND a.type IN ('revenue','expense')
        """
        if date_from:
            sql += " AND je.date >= :date_from\n"
        if date_to:
            sql += " AND je.date <= :date_to\n"

    rows = _exec_sql(sql, {'company_id': company_id, 'date_from': date_from, 'date_to': date_to})
    if rows is not None:
        return rows

    # Fallback: return empty
    return []


def ledger(company_id: str, account_id: Optional[str], date_from: Optional[str], date_to: Optional[str], page: int = 1, per_page: int = 20):
    # Paginated ledger - prefer DB
    sql = f"""
    SELECT jl.id as line_id, je.id as journal_id, je.date, jl.line_no, a.code as account_code, a.name as account_name, jl.debit, jl.credit, je.description
    FROM journal_lines jl
    JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
    JOIN accounts a ON a.id = jl.account_id
    WHERE a.company_id = :company_id
    """
    if account_id:
        sql += " AND a.id = :account_id\n"
    if date_from:
        sql += " AND je.date >= :date_from\n"
    if date_to:
        sql += " AND je.date <= :date_to\n"
    sql += " ORDER BY je.date DESC, je.id DESC"
    sql += " LIMIT :limit OFFSET :offset"

    params = {"company_id": company_id, "account_id": account_id, "date_from": date_from, "date_to": date_to, "limit": per_page, "offset": (page-1)*per_page}
    rows = _exec_sql(sql, params)
    if rows is not None:
        return rows

    # Fallback in-memory ledger
    res = []
    entries = gl_service.list_entries({'company_id': company_id, 'date_from': date_from, 'date_to': date_to}, page=1, per_page=100000).get('items', [])
    for e in entries:
        for ln in e.get('lines', []):
            if account_id and str(ln.get('account_id')) != str(account_id):
                continue
            res.append({'line_id': ln.get('id'), 'journal_id': e.get('id'), 'date': e.get('date'), 'line_no': ln.get('line_no'), 'debit': ln.get('debit'), 'credit': ln.get('credit'), 'description': ln.get('description')})
    # simple pagination
    total = len(res)
    start = (page-1)*per_page
    return {'items': res[start:start+per_page], 'total': total}
