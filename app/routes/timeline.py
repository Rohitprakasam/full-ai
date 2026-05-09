from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.models.timeline import TimelineEvent
from app.models.case import Case
from app.models.user import User
from app.schemas.timeline import TimelineEventCreate, TimelineEventOut
from app.utils.security import get_current_user
from beanie import PydanticObjectId

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.post("/event", response_model=TimelineEventOut)
async def create_event(event_in: TimelineEventCreate, current_user: User = Depends(get_current_user)):
    case = await Case.get(PydanticObjectId(event_in.case_id))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    event = TimelineEvent(
        case_id=PydanticObjectId(event_in.case_id),
        event_type=event_in.event_type,
        confidence_score=event_in.confidence_score,
        description=event_in.description
    )
    await event.insert()
    return event

@router.get("/{case_id}", response_model=List[TimelineEventOut])
async def get_case_timeline(case_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    # Sort events chronologically
    events = await TimelineEvent.find(TimelineEvent.case_id == case_id).sort("timestamp").to_list()
    return events
