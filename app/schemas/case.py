from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId

class CaseCreate(BaseModel):
    title: str
    crime_type: str

class CaseUpdate(BaseModel):
    status: Optional[str] = None
    risk_score: Optional[int] = None

class CaseOut(BaseModel):
    id: PydanticObjectId
    title: str
    crime_type: str
    status: str
    risk_score: int
    created_at: datetime
