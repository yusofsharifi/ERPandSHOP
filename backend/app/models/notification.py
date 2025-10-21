from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=True)
    type = Column(String, nullable=False, default='info')
    read = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('app.models.user.User', backref='notifications')
