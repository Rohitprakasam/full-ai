from typing import Optional, Dict, List
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class Evidence(Document):
    case_id: PydanticObjectId
    type: str
    hash: Optional[str] = None
    path: str
    uploaded_by: PydanticObjectId
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # --- Person 2 AI fields ---
    ai_summary: Optional[str] = None
    ai_entities: Optional[Dict] = None
    ai_raw_text: Optional[str] = None
    ai_status: str = "pending"  # pending | processing | complete | failed

    class Settings:
        name = "evidence"
