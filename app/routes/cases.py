from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.models.case import Case
from app.models.user import User
from app.schemas.case import CaseCreate, CaseUpdate, CaseOut
from app.utils.security import get_current_user
from beanie import PydanticObjectId

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=CaseOut)
async def create_case(case_in: CaseCreate, current_user: User = Depends(get_current_user)):
    case = Case(
        title=case_in.title,
        crime_type=case_in.crime_type
    )
    await case.insert()
    return case

@router.get("", response_model=List[CaseOut])
async def list_cases(current_user: User = Depends(get_current_user)):
    return await Case.find_all().to_list()

@router.get("/{case_id}", response_model=CaseOut)
async def get_case(case_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=CaseOut)
async def update_case(case_id: PydanticObjectId, case_in: CaseUpdate, current_user: User = Depends(get_current_user)):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case_in.status is not None:
        case.status = case_in.status
    if case_in.risk_score is not None:
        case.risk_score = case_in.risk_score
    await case.save()
    return case
