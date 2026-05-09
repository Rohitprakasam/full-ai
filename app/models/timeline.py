from typing import Optional
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class TimelineEvent(Document):
    case_id: PydanticObjectId
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    confidence_score: float = 1.0
    description: Optional[str] = None
    
    class Settings:
        name = "timeline_events"
