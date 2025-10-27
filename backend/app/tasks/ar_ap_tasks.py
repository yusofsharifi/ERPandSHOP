from datetime import date, datetime
from app.db.session import SessionLocal
from app.models.ar_ap import Invoice
from app.services.notification_service import create_notification, send_email_to_roles


def run_overdue_check():
    """Scan for overdue invoices and create notifications. Intended to be called by a scheduler or Celery beat."""
    db = SessionLocal()
    try:
        today = date.today()
        overdue = db.query(Invoice).filter(Invoice.due_date != None, Invoice.due_date < today, Invoice.status.in_(['open','partial'])).all()
        for inv in overdue:
            # create notification
            msg = f"Invoice {inv.invoice_no} is overdue"
            create_notification(db, title="Overdue Invoice", body=msg, level='warning', company_id=inv.company_id)
            # optional: send email to roles
            try:
                send_email_to_roles(db, role='accounting', subject='Overdue Invoice', body=msg)
            except Exception:
                pass
    finally:
        db.close()
