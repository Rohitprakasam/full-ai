"""Evidence Upload Route — Enhanced with real AI pipeline trigger.
Based on Person 1's upload.py, now fires actual AI processing instead of dummy task."""
import hashlib
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.models.evidence import Evidence
from app.models.case import Case
from app.models.user import User
from app.utils.security import get_current_user
from app.utils.storage import upload_file
from beanie import PydanticObjectId

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("/upload")
async def upload_evidence(
    case_id: PydanticObjectId = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    bucket_name = f"case-{str(case_id)}"
    object_name = f"{file_hash}_{file.filename}"

    # Upload to MinIO
    await run_in_threadpool(
        upload_file,
        bucket_name=bucket_name,
        object_name=object_name,
        data=file_bytes,
        content_type=file.content_type
    )

    # Save metadata to MongoDB
    evidence = Evidence(
        case_id=case_id,
        type=type,
        hash=file_hash,
        path=f"{bucket_name}/{object_name}",
        uploaded_by=current_user.id,
        ai_status="pending"
    )
    await evidence.insert()

    # Fire real AI processing pipeline (Person 2's contribution)
    from app.workers.tasks import process_evidence_task
    process_evidence_task.delay(str(evidence.id), str(case_id), type)

    return {
        "status": "success",
        "evidence_id": str(evidence.id),
        "hash": file_hash,
        "path": evidence.path,
        "ai_status": "processing"
    }


@router.get("/case/{case_id}")
async def get_case_evidence(case_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    evidence = await Evidence.find(Evidence.case_id == case_id).to_list()
    return evidence


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    evidence = await Evidence.get(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence
