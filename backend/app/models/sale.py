from sqlalchemy import Column, Integer, Float, String, DateTime
from app.db.base import Base
from datetime import datetime

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, default=0.0)
    currency = Column(String, default='USD')
    created_at = Column(DateTime, default=datetime.utcnow)
