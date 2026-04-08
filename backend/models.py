from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NodeBase(BaseModel):
    id: int
    type: str  # hospital / traffic
    lat: float
    lng: float
    water_level: int = Field(ge=0, le=100)
    power: int = Field(ge=0, le=100)
    status: str  # "NORMAL", "WARNING", "CRITICAL"
    timestamp: Optional[datetime] = None

class NodeResponse(NodeBase):
    pass
