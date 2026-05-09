from typing import Optional
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class AuditLog(Document):
    user_id: PydanticObjectId
    action: str
    resource: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "audit_logs"
