from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from datetime import datetime

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
