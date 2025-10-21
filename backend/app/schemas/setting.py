from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SettingBase(BaseModel):
    key: str
    value: Optional[str]
    category: Optional[str] = 'General'
    data_type: Optional[str] = 'str'
    translations: Optional[Dict[str, str]] = None

class SettingRead(SettingBase):
    id: int
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class SettingBulkItem(BaseModel):
    key: str
    value: Any

class SettingBulkUpdate(BaseModel):
    items: List[SettingBulkItem]
