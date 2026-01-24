from typing import Any, Dict, List, Optional
from app.reports.reports_sql import fn_trial_balance, fn_account_ledger, fn_balance_sheet, fn_pnl, fn_cashflow
from sqlalchemy.orm import Session
from app.core.config import settings
from app.utils.cache import get_cache_or_compute
import json


class ReportsService:
    def trial_balance(self, db: Session, company_id: str, as_of_date: str, include_zero: bool = False, currency: Optional[str] = None) -> Dict[str, Any]:
        cache_key = f"trial_balance:{company_id}:{as_of_date}:{currency}:{include_zero}"
        def compute():
            res = fn_trial_balance(db, company_id, as_of_date)
            # Optionally filter zero balances
            try:
                if include_zero:
                    return res
                # filter accounts with closing != 0
                obj = res
                if not obj or 'accounts' not in obj:
                    return res
                filtered = [a for a in obj.get('accounts', []) if (a.get('closing_balance') or 0) != 0]
                obj['accounts'] = filtered
                return obj
            except Exception:
                return res
        # cache using helper
        result = get_cache_or_compute(cache_key, compute, ttl=60)
        # get_cache_or_compute may be async; ensure return value
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(result)
        return result

    def account_ledger(self, db: Session, company_id: str, account_id: str, date_from: Optional[str], date_to: Optional[str], page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        per_page = min(per_page, 1000)
        rows = fn_account_ledger(db, company_id, account_id, date_from, date_to, page, per_page)
        total = len(rows)
        return {'rows': rows, 'page': page, 'per_page': per_page, 'returned': total}

    def balance_sheet(self, db: Session, company_id: str, as_of_date: str) -> List[Dict[str, Any]]:
        return fn_balance_sheet(db, company_id, as_of_date)

    def pnl(self, db: Session, company_id: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        return fn_pnl(db, company_id, date_from, date_to)

    def cashflow(self, db: Session, company_id: str, date_from: str, date_to: str, method: str = 'direct') -> List[Dict[str, Any]]:
        return fn_cashflow(db, company_id, date_from, date_to, method)


reports_service = ReportsService()
