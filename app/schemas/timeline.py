from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId

class TimelineEventCreate(BaseModel):
    case_id: str
    event_type: str
    confidence_score: float = 1.0
    description: Optional[str] = None

class TimelineEventOut(BaseModel):
    id: PydanticObjectId
    case_id: PydanticObjectId
    timestamp: datetime
    event_type: str
    confidence_score: float
    description: Optional[str] = None
