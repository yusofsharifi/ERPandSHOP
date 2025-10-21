from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class TwoFACode(Base):
    __tablename__ = 'two_fa_codes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    code = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('app.models.user.User', backref='two_fa_codes')
