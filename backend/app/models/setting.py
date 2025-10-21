from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from app.db.base import Base
from datetime import datetime
import enum

class SettingCategory(str, enum.Enum):
    GENERAL = 'General'
    EMAIL = 'Email'
    SECURITY = 'Security'
    FINANCIAL = 'Financial'

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    category = Column(Enum(SettingCategory), default=SettingCategory.GENERAL)
    data_type = Column(String, default='str')  # 'str', 'int', 'bool'
    translations = Column(JSON, nullable=True)  # e.g. {"en": "Label", "fa": "برچسب"}
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
