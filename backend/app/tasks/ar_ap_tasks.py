from datetime import date, datetime
from app.db.session import SessionLocal
from app.models.ar_ap import Invoice
from app.services.notification_service import send_to_role


def run_overdue_check():
    """Scan for overdue invoices and create notifications. Intended to be called by a scheduler or Celery beat."""
    db = SessionLocal()
    try:
        today = date.today()
        overdue = db.query(Invoice).filter(Invoice.due_date != None, Invoice.due_date < today, Invoice.status.in_(['open','partial'])).all()
        for inv in overdue:
            msg = f"Invoice {inv.invoice_no} is overdue"
            try:
                send_to_role(db, 'Accounting', 'Overdue invoice', msg, type='warning', email_alert=False)
            except Exception:
                pass
    finally:
        db.close()
