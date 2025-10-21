from typing import Dict, List, Tuple, Optional, Any
from uuid import uuid4, UUID
from threading import Lock
from datetime import datetime, date
from app.schemas import gl as gl_schemas
import csv
import io
import os
from app.core.config import settings

# In-memory stores
_accounts: Dict[UUID, Dict] = {}
_entries: Dict[UUID, Dict] = {}
_sequences: Dict[Tuple[str, int], int] = {}
_attachments: Dict[UUID, List[Dict]] = {}
_audit: List[Dict] = []

_lock = Lock()

UPLOAD_DIR = getattr(settings, "UPLOAD_DIR", "uploads")
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception:
        pass

class GLService:
    @staticmethod
    def list_accounts(company_id=None, search=None, type=None, parent_id=None, page=1, per_page=50):
        items = list(_accounts.values())
        if company_id:
            items = [i for i in items if str(i.get("company_id")) == str(company_id)]
        if search:
            items = [i for i in items if search.lower() in (i.get("name","") or "").lower() or search.lower() in (i.get("code","") or "").lower()]
        if type:
            items = [i for i in items if i.get("type") == type]
        if parent_id:
            items = [i for i in items if i.get("parent_id") == parent_id]
        total = len(items)
        start = (page-1)*per_page
        end = start + per_page
        return {"items": items[start:end], "total": total}

    @staticmethod
    def create_account(data: gl_schemas.AccountIn, created_by: Optional[UUID]=None):
        # unique code per company
        for a in _accounts.values():
            if str(a["company_id"]) == str(data.company_id) and a["code"] == data.code:
                raise ValueError("duplicate_account_code")
        aid = uuid4()
        now = datetime.utcnow().isoformat()
        rec = {
            "id": aid,
            "company_id": data.company_id,
            "code": data.code,
            "name": data.name,
            "type": data.type,
            "parent_id": data.parent_id,
            "is_active": True,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now
        }
        _accounts[aid] = rec
        GLService._audit("account", aid, "create", rec, performed_by=created_by)
        return rec

    @staticmethod
    def update_account(account_id: UUID, data: gl_schemas.AccountIn, updated_by: Optional[UUID]=None):
        rec = _accounts.get(account_id)
        if not rec:
            raise KeyError("account_not_found")
        # ensure unique code
        for a_id, a in _accounts.items():
            if a_id != account_id and str(a["company_id"]) == str(data.company_id) and a["code"] == data.code:
                raise ValueError("duplicate_account_code")
        rec.update({
            "code": data.code,
            "name": data.name,
            "type": data.type,
            "parent_id": data.parent_id,
            "updated_at": datetime.utcnow().isoformat()
        })
        GLService._audit("account", account_id, "update", rec, performed_by=updated_by)
        return rec

    @staticmethod
    def soft_delete_account(account_id: UUID, deleted_by: Optional[UUID]=None):
        rec = _accounts.get(account_id)
        if not rec:
            raise KeyError("account_not_found")
        rec["is_active"] = False
        rec["updated_at"] = datetime.utcnow().isoformat()
        GLService._audit("account", account_id, "delete", rec, performed_by=deleted_by)
        return rec

    @staticmethod
    def create_journal_entry(payload: gl_schemas.JournalEntryCreate, created_by: Optional[UUID]=None):
        # Validate accounts exist and amounts
        total_debit = 0
        total_credit = 0
        for ln in payload.lines:
            if str(ln.account_id) not in [str(aid) for aid in _accounts.keys()]:
                raise KeyError("account_not_found")
            total_debit += float(ln.debit)
            total_credit += float(ln.credit)
        eid = uuid4()
        now = datetime.utcnow().isoformat()
        rec = {
            "id": eid,
            "company_id": payload.company_id,
            "number": None,
            "fiscal_year": payload.fiscal_year,
            "period": payload.period,
            "date": str(payload.date),
            "description": payload.description,
            "total_debit": round(total_debit,2),
            "total_credit": round(total_credit,2),
            "status": "draft",
            "original_entry_id": None,
            "created_by": created_by,
            "approved_by": None,
            "created_at": now,
            "posted_at": None,
            "lines": [ln.dict() for ln in payload.lines],
            "attachments": payload.attachments or []
        }
        _entries[eid] = rec
        GLService._audit("journal_entry", eid, "create", rec, performed_by=created_by)
        return rec

    @staticmethod
    def update_journal_entry(entry_id: UUID, payload: gl_schemas.JournalEntryCreate, updated_by: Optional[UUID]=None):
        rec = _entries.get(entry_id)
        if not rec:
            raise KeyError("entry_not_found")
        if rec.get("status") != "draft":
            raise ValueError("cannot_update_non_draft")
        # Check lock
        locked_by = rec.get("locked_by")
        locked_at = rec.get("locked_at")
        # expire locks older than 15 minutes
        if locked_by and locked_at:
            try:
                locked_time = datetime.fromisoformat(locked_at)
                if (datetime.utcnow() - locked_time).total_seconds() > 15*60:
                    # expire lock
                    rec.pop("locked_by", None)
                    rec.pop("locked_at", None)
                elif str(locked_by) != str(updated_by):
                    raise ValueError("locked_by_other")
            except Exception:
                pass
        total_debit = sum([float(l.debit) for l in payload.lines])
        total_credit = sum([float(l.credit) for l in payload.lines])
        rec.update({
            "fiscal_year": payload.fiscal_year,
            "period": payload.period,
            "date": str(payload.date),
            "description": payload.description,
            "total_debit": round(total_debit,2),
            "total_credit": round(total_credit,2),
            "lines": [ln.dict() for ln in payload.lines],
            "attachments": payload.attachments or [],
            "updated_at": datetime.utcnow().isoformat()
        })
        GLService._audit("journal_entry", entry_id, "update", rec, performed_by=updated_by)
        return rec

    @staticmethod
    def lock_entry(entry_id: UUID, user_id: Optional[UUID]=None):
        rec = _entries.get(entry_id)
        if not rec:
            raise KeyError("entry_not_found")
        # if locked by other and not expired, raise
        locked_by = rec.get("locked_by")
        locked_at = rec.get("locked_at")
        if locked_by and locked_at:
            try:
                locked_time = datetime.fromisoformat(locked_at)
                if (datetime.utcnow() - locked_time).total_seconds() <= 15*60 and str(locked_by) != str(user_id):
                    raise ValueError("locked_by_other")
            except ValueError:
                raise
            except Exception:
                pass
        rec["locked_by"] = user_id
        rec["locked_at"] = datetime.utcnow().isoformat()
        GLService._audit("journal_entry", entry_id, "lock", {"locked_by": user_id}, performed_by=user_id)
        return {"locked_by": user_id, "locked_at": rec["locked_at"]}

    @staticmethod
    def unlock_entry(entry_id: UUID, user_id: Optional[UUID]=None):
        rec = _entries.get(entry_id)
        if not rec:
            raise KeyError("entry_not_found")
        locked_by = rec.get("locked_by")
        if not locked_by:
            return {"unlocked": True}
        if str(locked_by) != str(user_id) and user_id != 'admin':
            raise ValueError("cannot_unlock_other")
        rec.pop("locked_by", None)
        rec.pop("locked_at", None)
        GLService._audit("journal_entry", entry_id, "unlock", {"unlocked_by": user_id}, performed_by=user_id)
        return {"unlocked": True}

    @staticmethod
    def post_journal_entry(entry_id: UUID, performed_by: Optional[UUID]=None):
        with _lock:
            rec = _entries.get(entry_id)
            if not rec:
                raise KeyError("entry_not_found")
            if rec.get("status") != "draft":
                raise ValueError("cannot_post_non_draft")
            total_debit = float(rec.get("total_debit",0))
            total_credit = float(rec.get("total_credit",0))
            if round(total_debit,2) != round(total_credit,2):
                raise ValueError("not_balanced")
            key = (str(rec["company_id"]), int(rec["fiscal_year"]))
            last = _sequences.get(key, 0)
            last += 1
            _sequences[key] = last
            rec["number"] = last
            rec["status"] = "posted"
            rec["posted_at"] = datetime.utcnow().isoformat()
            rec["approved_by"] = performed_by
            GLService._audit("journal_entry", entry_id, "post", rec, performed_by=performed_by)
            return rec

    @staticmethod
    def reverse_entry(entry_id: UUID, performed_by: Optional[UUID]=None, auto_post: bool=True):
        with _lock:
            orig = _entries.get(entry_id)
            if not orig:
                raise KeyError("entry_not_found")
            # create reversed lines
            rev_lines = []
            for ln in orig.get("lines",[]):
                rev_lines.append({
                    "line_no": ln.get("line_no"),
                    "account_id": ln.get("account_id"),
                    "description": f"Reversal of {orig.get('id')}: {ln.get('description')}",
                    "debit": ln.get("credit",0),
                    "credit": ln.get("debit",0),
                    "cost_center_id": ln.get("cost_center_id"),
                    "analytic_tags": ln.get("analytic_tags")
                })
            payload = gl_schemas.JournalEntryCreate(
                company_id=orig.get("company_id"),
                fiscal_year=orig.get("fiscal_year"),
                period=orig.get("period"),
                date=orig.get("date"),
                description=f"Reversal of {orig.get('id')}",
                lines=[gl_schemas.JournalLineIn(**l) for l in rev_lines]
            )
            rev = GLService.create_journal_entry(payload, created_by=performed_by)
            rev["original_entry_id"] = orig.get("id")
            GLService._audit("journal_entry", rev.get("id"), "reverse_create", rev, performed_by=performed_by)
            if auto_post:
                GLService.post_journal_entry(rev.get("id"), performed_by=performed_by)
            return rev

    @staticmethod
    def list_entries(filters: dict, page=1, per_page=20):
        items = list(_entries.values())
        # apply basic filters
        company_id = filters.get("company_id")
        if company_id:
            items = [i for i in items if str(i.get("company_id")) == str(company_id)]
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if date_from:
            items = [i for i in items if i.get("date") >= str(date_from)]
        if date_to:
            items = [i for i in items if i.get("date") <= str(date_to)]
        status = filters.get("status")
        if status:
            items = [i for i in items if i.get("status") == status]
        total = len(items)
        start = (page-1)*per_page
        return {"items": items[start:start+per_page], "total": total}

    @staticmethod
    def get_entry(entry_id: UUID):
        rec = _entries.get(entry_id)
        if not rec:
            raise KeyError("entry_not_found")
        return rec

    @staticmethod
    def trial_balance(company_id: UUID, date_to: Optional[str]=None):
        # aggregate by account
        agg = {}
        for e in _entries.values():
            if str(e.get("company_id")) != str(company_id):
                continue
            if date_to and e.get("date") > date_to:
                continue
            for ln in e.get("lines",[]):
                acc = str(ln.get("account_id"))
                d = float(ln.get("debit",0))
                c = float(ln.get("credit",0))
                if acc not in agg:
                    agg[acc] = {"debit":0.0, "credit":0.0}
                agg[acc]["debit"] += d
                agg[acc]["credit"] += c
        result = []
        for acc_id, vals in agg.items():
            result.append({"account_id": acc_id, "debit": round(vals["debit"],2), "credit": round(vals["credit"],2)})
        return result

    @staticmethod
    def add_attachment(entry_id: UUID, filename: str, storage_path: str, uploaded_by: Optional[UUID]=None):
        if entry_id not in _entries:
            raise KeyError("entry_not_found")
        item = {"id": uuid4(), "filename": filename, "storage_path": storage_path, "uploaded_by": uploaded_by, "uploaded_at": datetime.utcnow().isoformat()}
        _attachments.setdefault(entry_id, []).append(item)
        # also add to entry attachments meta
        _entries[entry_id].setdefault("attachments", []).append(filename)
        GLService._audit("attachment", entry_id, "upload", item, performed_by=uploaded_by)
        return item

    @staticmethod
    def list_attachments(entry_id: UUID):
        if entry_id not in _entries:
            raise KeyError("entry_not_found")
        return _attachments.get(entry_id, [])

    @staticmethod
    def import_entries_from_csv(file_bytes: bytes, dry_run: bool = True, created_by: Optional[UUID]=None):
        text = file_bytes.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        # Expect column 'entry_ref' to group lines
        grouped: Dict[str, List[Dict[str,str]]] = {}
        errors: List[Dict[str,Any]] = []
        for i, r in enumerate(rows):
            ref = r.get('entry_ref') or r.get('reference') or str(i)
            grouped.setdefault(ref, []).append({k:v for k,v in r.items()})
        previews = []
        for ref, group in grouped.items():
            lines = []
            example = group[0]
            company_id = example.get('company_id')
            fiscal_year = int(example.get('fiscal_year') or example.get('year') or 0)
            period = example.get('period') or ''
            date_val = example.get('date') or example.get('transaction_date')
            description = example.get('description') or ''
            for idx, row in enumerate(group):
                try:
                    ln = {
                        'line_no': idx+1,
                        'account_id': UUID(row.get('account_id')) if row.get('account_id') else None,
                        'description': row.get('line_description') or row.get('description') or '',
                        'debit': float(row.get('debit') or 0),
                        'credit': float(row.get('credit') or 0),
                        'cost_center_id': row.get('cost_center_id') or None,
                        'analytic_tags': None
                    }
                    if not ln['account_id']:
                        raise ValueError('account_id_missing')
                    lines.append(gl_schemas.JournalLineIn(**ln))
                except Exception as e:
                    errors.append({'row': idx+1, 'error': str(e), 'data': row})
            if lines:
                je = {
                    'entry_ref': ref,
                    'company_id': company_id,
                    'fiscal_year': fiscal_year,
                    'period': period,
                    'date': date_val,
                    'description': description,
                    'lines': [l.dict() for l in lines]
                }
                previews.append(je)
        result = {'previews': previews, 'errors': errors}
        created = []
        if not dry_run and not errors:
            for p in previews:
                payload = gl_schemas.JournalEntryCreate(
                    company_id=UUID(p['company_id']),
                    fiscal_year=int(p['fiscal_year']),
                    period=p['period'] or '',
                    date=p['date'],
                    description=p['description'],
                    lines=[gl_schemas.JournalLineIn(**l) for l in p['lines']]
                )
                rec = GLService.create_journal_entry(payload, created_by=created_by)
                created.append(rec)
        return {'result': result, 'created': created}

    @staticmethod
    def export_entry_csv(entry_id: UUID) -> str:
        rec = _entries.get(entry_id)
        if not rec:
            raise KeyError('entry_not_found')
        output = io.StringIO()
        writer = csv.writer(output)
        # header
        writer.writerow(['line_no','account_id','description','debit','credit','cost_center_id'])
        for ln in rec.get('lines',[]):
            writer.writerow([ln.get('line_no'), ln.get('account_id'), ln.get('description'), ln.get('debit'), ln.get('credit'), ln.get('cost_center_id')])
        return output.getvalue()

    @staticmethod
    def trial_balance(company_id: UUID, date_to: Optional[str]=None):
        # aggregate by account
        agg = {}
        for e in _entries.values():
            if str(e.get("company_id")) != str(company_id):
                continue
            if date_to and e.get("date") > date_to:
                continue
            for ln in e.get("lines",[]):
                acc = str(ln.get("account_id"))
                d = float(ln.get("debit",0))
                c = float(ln.get("credit",0))
                if acc not in agg:
                    agg[acc] = {"debit":0.0, "credit":0.0}
                agg[acc]["debit"] += d
                agg[acc]["credit"] += c
        result = []
        for acc_id, vals in agg.items():
            result.append({"account_id": acc_id, "debit": round(vals["debit"],2), "credit": round(vals["credit"],2)})
        return result

    @staticmethod
    def _audit(resource_type, resource_id, action, payload, performed_by=None):
        _audit.append({
            "id": uuid4(),
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "payload": payload,
            "performed_by": performed_by,
            "performed_at": datetime.utcnow().isoformat()
        })

# Export a singleton
gl_service = GLService()
