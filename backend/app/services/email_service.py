from app.core.config import settings
from typing import Optional
import smtplib
from email.message import EmailMessage


def send_email(to: str, subject: str, body: str) -> bool:
    # Minimal stub - integrate real SMTP in production using settings.SMTP_* values
    print(f"Sending email to {to}: {subject}")
    return True


def test_smtp(host: str, port: int, user: str, password: str, use_tls: bool = True, from_email: Optional[str] = None) -> dict:
    """Attempt to connect and send a test email. Returns dict with success and message."""
    try:
        msg = EmailMessage()
        msg['Subject'] = 'SMTP Test'
        msg['From'] = from_email or settings.SMTP_USER or 'test@example.com'
        msg['To'] = msg['From']
        msg.set_content('This is a test email from BizGenius SMTP test')

        if use_tls:
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
            server.login(user, password)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            # try login if credentials provided
            if user and password:
                server.login(user, password)
        server.send_message(msg)
        server.quit()
        return {"ok": True, "message": "Test email sent"}
    except Exception as e:
        return {"ok": False, "message": str(e)}
