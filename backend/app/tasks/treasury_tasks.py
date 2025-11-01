from datetime import datetime
from app.db.session import SessionLocal
from app.services import treasury_service
from app.services.notification_service import send_to_role


from backend.celery_app import celery_app

@celery_app.task(name='treasury.daily_reconciliation')
def daily_reconciliation_job():
    db = SessionLocal()
    try:
        # placeholder: notify treasury team to run reconciliations
        send_to_role(db, 'Treasury', 'Daily reconciliation reminder', 'Please review pending reconciliations', type='info', email_alert=False)
    finally:
        db.close()


def low_balance_check(threshold_map: dict):
    db = SessionLocal()
    try:
        # threshold_map: {company_id: threshold_amount}
        from app.models.treasury import CashAccount, BankAccount
        for company_id, thr in threshold_map.items():
            thr = float(thr)
            cash = db.query(CashAccount).filter(CashAccount.company_id == company_id).all()
            for c in cash:
                if float(c.balance or 0) < thr:
                    send_to_role(db, 'Treasury', 'Low balance alert', f'Account {c.name} is below threshold', type='warning', email_alert=False)
    finally:
        db.close()
