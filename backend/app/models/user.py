from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    role = relationship('Role', back_populates='users')
    created_at = Column(DateTime, default=datetime.utcnow)
    # relationships
    refresh_tokens = relationship('RefreshToken', back_populates='user')
    notifications = relationship('Notification', back_populates='user')
