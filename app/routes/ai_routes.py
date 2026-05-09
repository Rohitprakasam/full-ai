"""AI Analysis Routes — Trigger and retrieve AI processing results."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.models.evidence import Evidence

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


class ManualAnalysisRequest(BaseModel):
    evidence_id: str
    case_id: str = ""


@router.post("/analyze/evidence")
async def trigger_ai_analysis(req: ManualAnalysisRequest):
    """Manually trigger AI analysis on an evidence item."""
    evidence = await Evidence.get(PydanticObjectId(req.evidence_id))
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    from app.workers.tasks import process_evidence_task
    process_evidence_task.delay(req.evidence_id, req.case_id or str(evidence.case_id), evidence.type)

    evidence.ai_status = "processing"
    await evidence.save()
    return {"status": "processing", "evidence_id": req.evidence_id}


@router.get("/status/{evidence_id}")
async def get_ai_status(evidence_id: PydanticObjectId):
    """Check AI processing status for an evidence item."""
    evidence = await Evidence.get(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {
        "evidence_id": str(evidence_id),
        "ai_status": evidence.ai_status,
        "ai_summary": evidence.ai_summary,
        "ai_entities": evidence.ai_entities
    }
