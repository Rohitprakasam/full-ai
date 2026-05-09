from typing import Optional, List, Dict
from datetime import datetime
from beanie import Document
from pydantic import Field

class Case(Document):
    title: str
    crime_type: str
    status: str = "open"
    risk_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Person 2 AI fields ---
    ai_risk_level: Optional[str] = None  # LOW | MEDIUM | HIGH | CRITICAL
    ai_risk_flags: Optional[List[str]] = None
    ai_risk_recommendation: Optional[str] = None

    class Settings:
        name = "cases"
