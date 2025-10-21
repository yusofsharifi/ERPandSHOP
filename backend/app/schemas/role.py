from pydantic import BaseModel
from typing import Optional, Dict, Any

class RoleBase(BaseModel):
    name: str
    description: Optional[str]
    permissions: Optional[Dict[str, Any]] = None

class RoleRead(RoleBase):
    id: int

    class Config:
        orm_mode = True
