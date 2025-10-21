from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.user import User
from app.models.notification import Notification

# Optional imports
try:
    from app.models.sale import Sale
    from app.models.inventory_item import InventoryItem
except Exception:
    Sale = None
    InventoryItem = None


def get_dashboard_stats(db: Session, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict[str, Any]:
    # Users count
    q = db.query(func.count(User.id))
    if start:
        q = q.filter(User.created_at >= start)
    if end:
        q = q.filter(User.created_at <= end)
    users_count = q.scalar() or 0

    # Sales total
    sales_total = 0.0
    if Sale is not None:
        sq = db.query(func.coalesce(func.sum(Sale.amount), 0.0))
        if start:
            sq = sq.filter(Sale.created_at >= start)
        if end:
            sq = sq.filter(Sale.created_at <= end)
        sales_total = float(sq.scalar() or 0.0)

    # Inventory count (sum quantities)
    inventory_count = 0
    if InventoryItem is not None:
        iq = db.query(func.coalesce(func.sum(InventoryItem.quantity), 0))
        inventory_count = int(iq.scalar() or 0)

    # Notifications unread
    nq = db.query(func.count(Notification.id)).filter(Notification.read == False)
    if start:
        nq = nq.filter(Notification.created_at >= start)
    if end:
        nq = nq.filter(Notification.created_at <= end)
    notifications_unread = nq.scalar() or 0

    return {
        'users_count': int(users_count),
        'sales_total': sales_total,
        'inventory_count': int(inventory_count),
        'notifications_unread': int(notifications_unread),
    }
