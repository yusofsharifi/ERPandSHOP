from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(JSON, nullable=True)  # e.g. {"users:create": true}
    users = relationship('User', back_populates='role')
