from fastapi import APIRouter, Depends, HTTPException, Query, Body, status, Request
from typing import Optional, List
from uuid import UUID, uuid4
from app.schemas import gl as gl_schemas
from app.services.gl_service import gl_service
from app.core.config import settings

router = APIRouter()

# Simple mock current_user dependency
def get_current_user(request: Request):
    # In absence of auth DB, read headers
    user_id = request.headers.get("X-User-Id")
    roles = request.headers.get("X-User-Roles", "").split(",") if request.headers.get("X-User-Roles") else []
    return {"id": user_id, "roles": roles}

def require_role(user, role: str):
    if not user:
        raise HTTPException(status_code=401, detail={"code":"unauthorized","message":{"fa":"ناشناس","en":"Unauthorized"}})
    if role not in user.get("roles",[]) and "admin" not in user.get("roles",[]):
        raise HTTPException(status_code=403, detail={"code":"forbidden","message":{"fa":"دسترسی کافی نیست","en":"Forbidden"}})

# Accounts endpoints
@router.get("/accounts")
def list_accounts(company_id: Optional[UUID] = Query(None), search: Optional[str]=Query(None), type: Optional[str]=Query(None), parent_id: Optional[UUID]=Query(None), page: int=1, per_page: int=50):
    res = gl_service.list_accounts(company_id=company_id, search=search, type=type, parent_id=parent_id, page=page, per_page=per_page)
    return res

@router.post("/accounts", status_code=201)
def create_account(payload: gl_schemas.AccountIn, current_user=Depends(get_current_user)):
    try:
        rec = gl_service.create_account(payload, created_by=current_user.get("id"))
        return rec
    except ValueError as e:
        if str(e) == "duplicate_account_code":
            raise HTTPException(status_code=409, detail={"code":"duplicate_account_code","message":{"fa":"کد حساب تکراری است","en":"Duplicate account code"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.put("/accounts/{account_id}")
def update_account(account_id: UUID, payload: gl_schemas.AccountIn, current_user=Depends(get_current_user)):
    try:
        rec = gl_service.update_account(account_id, payload, updated_by=current_user.get("id"))
        return rec
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"account_not_found","message":{"fa":"حساب یافت نشد","en":"Account not found"}})
    except ValueError as e:
        if str(e) == "duplicate_account_code":
            raise HTTPException(status_code=409, detail={"code":"duplicate_account_code","message":{"fa":"کد حساب تکراری است","en":"Duplicate account code"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.delete("/accounts/{account_id}")
def delete_account(account_id: UUID, current_user=Depends(get_current_user)):
    try:
        rec = gl_service.soft_delete_account(account_id, deleted_by=current_user.get("id"))
        return {"code":"ok","message":{"fa":"حذف شد","en":"Deleted"}, "account": rec}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"account_not_found","message":{"fa":"حساب یافت نشد","en":"Account not found"}})

# Journal entries
@router.get("/journal-entries")
def list_entries(company_id: Optional[UUID]=Query(None), date_from: Optional[str]=Query(None), date_to: Optional[str]=Query(None), status: Optional[str]=Query(None), account_id: Optional[UUID]=Query(None), full_text: Optional[str]=Query(None), page: int=1, per_page: int=20):
    filters = {"company_id": company_id, "date_from": date_from, "date_to": date_to, "status": status, "account_id": account_id, "full_text": full_text}
    res = gl_service.list_entries(filters, page=page, per_page=per_page)
    return res

@router.get("/journal-entries/{entry_id}")
def get_entry(entry_id: UUID):
    try:
        rec = gl_service.get_entry(entry_id)
        return rec
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})

@router.post("/journal-entries", status_code=201)
def create_entry(payload: gl_schemas.JournalEntryCreate, current_user=Depends(get_current_user)):
    try:
        rec = gl_service.create_journal_entry(payload, created_by=current_user.get("id"))
        return rec
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"account_not_found","message":{"fa":"حساب یافت نشد","en":"Account not found"}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.put("/journal-entries/{entry_id}")
def update_entry(entry_id: UUID, payload: gl_schemas.JournalEntryCreate, current_user=Depends(get_current_user)):
    try:
        rec = gl_service.update_journal_entry(entry_id, payload, updated_by=current_user.get("id"))
        return rec
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})
    except ValueError as e:
        if str(e) == "cannot_update_non_draft":
            raise HTTPException(status_code=409, detail={"code":"cannot_update_non_draft","message":{"fa":"قابل ویرایش نیست","en":"Cannot update non-draft entry"}})
        if str(e) == "locked_by_other":
            raise HTTPException(status_code=423, detail={"code":"locked","message":{"fa":"سند توسط کاربر دیگری قفل شده است","en":"Entry locked by another user"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.post("/journal-entries/{entry_id}/lock")
def lock_entry(entry_id: UUID, current_user=Depends(get_current_user)):
    try:
        res = gl_service.lock_entry(entry_id, user_id=current_user.get("id"))
        return {"code":"ok","lock": res}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})
    except ValueError as e:
        if str(e) == "locked_by_other":
            raise HTTPException(status_code=423, detail={"code":"locked","message":{"fa":"سند توسط کاربر دیگری قفل شده است","en":"Entry locked by another user"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.post("/journal-entries/{entry_id}/unlock")
def unlock_entry(entry_id: UUID, current_user=Depends(get_current_user)):
    try:
        res = gl_service.unlock_entry(entry_id, user_id=current_user.get("id"))
        return {"code":"ok","result": res}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})
    except ValueError as e:
        if str(e) == "cannot_unlock_other":
            raise HTTPException(status_code=403, detail={"code":"forbidden","message":{"fa":"نمی‌توانید قفل کاربر دیگر را بردارید","en":"Cannot unlock entry locked by another user"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.post("/journal-entries/{entry_id}/post")
def post_entry(entry_id: UUID, current_user=Depends(get_current_user)):
    # permission require finance_post
    user = current_user
    try:
        require_role(user, "finance_post")
        rec = gl_service.post_journal_entry(entry_id, performed_by=user.get("id"))
        return {"code":"ok","message":{"fa":"سند با موفقیت ثبت شد","en":"Journal entry posted successfully"}, "entry": rec}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})
    except ValueError as e:
        if str(e) == "not_balanced":
            raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":"جمع بدهکاری و بستانکاری برابر نیست","en":"Total debit and credit must match"}})
        if str(e) == "cannot_post_non_draft":
            raise HTTPException(status_code=409, detail={"code":"cannot_post","message":{"fa":"قابل پست نیست","en":"Entry is not in draft state"}})
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.post("/journal-entries/{entry_id}/reverse")
def reverse_entry(entry_id: UUID, current_user=Depends(get_current_user), auto_post: bool = Body(True)):
    try:
        rec = gl_service.reverse_entry(entry_id, performed_by=current_user.get("id"), auto_post=auto_post)
        return {"code":"ok","message":{"fa":"برگشت سند ایجاد شد","en":"Reversal entry created"}, "entry": rec}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code":"validation_error","message":{"fa":str(e),"en":str(e)}})

@router.get("/reports/trial-balance")
def trial_balance(company_id: UUID = Query(...), date_to: Optional[str] = Query(None)):
    res = gl_service.trial_balance(company_id, date_to=date_to)
    return {"items": res}


# Attachments upload
from fastapi import UploadFile, File

@router.post("/journal-entries/{entry_id}/attachments")
async def upload_attachment(entry_id: UUID, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    try:
        # Save file to uploads dir
        filename = file.filename
        save_path = f"{settings.UPLOAD_DIR}/{uuid4()}_{filename}"
        contents = await file.read()
        try:
            with open(save_path, "wb") as f:
                f.write(contents)
        except Exception:
            # fallback to memory-only
            save_path = f"in-memory://{filename}"
        item = gl_service.add_attachment(entry_id, filename, save_path, uploaded_by=current_user.get("id"))
        return {"code":"ok","attachment": item}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})

# List attachments
@router.get("/journal-entries/{entry_id}/attachments")
def list_attachments(entry_id: UUID):
    try:
        items = gl_service.list_attachments(entry_id)
        return {"items": items}
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})

# Export entry as CSV
from fastapi.responses import PlainTextResponse

@router.get("/journal-entries/{entry_id}/export")
def export_entry(entry_id: UUID):
    try:
        csv_text = gl_service.export_entry_csv(entry_id)
        return PlainTextResponse(content=csv_text, media_type='text/csv')
    except KeyError:
        raise HTTPException(status_code=404, detail={"code":"entry_not_found","message":{"fa":"سند یافت نشد","en":"Entry not found"}})

# Import entries from CSV (dry run or commit)
@router.post("/journal-entries/import")
async def import_entries(file: UploadFile = File(...), dry_run: bool = Query(True), current_user=Depends(get_current_user)):
    try:
        contents = await file.read()
        res = gl_service.import_entries_from_csv(contents, dry_run=dry_run, created_by=current_user.get("id"))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail={"code":"import_error","message":{"fa":str(e),"en":str(e)}})
