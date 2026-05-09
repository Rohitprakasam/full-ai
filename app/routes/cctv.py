"""CCTV Analytics Routes — Upload and analyze CCTV footage."""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import shutil, uuid, os
from app.config import settings

router = APIRouter(prefix="/cctv", tags=["CCTV Analytics"])

# In-memory store for demo (swap with MongoDB in production)
_cctv_results = {}


@router.post("/analyze/{case_id}")
async def analyze_cctv(case_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and analyze CCTV footage for a case."""
    video_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}.mp4")

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(_run_cctv_pipeline, case_id, save_path, video_id)
    return {"status": "processing", "video_id": video_id, "case_id": case_id}


@router.get("/events/{case_id}")
async def get_cctv_events(case_id: str):
    """Get all CCTV analysis events for a case."""
    result = _cctv_results.get(case_id, {})
    return {
        "case_id": case_id,
        "events": result.get("events", []),
        "flags": result.get("flags", []),
        "summary": result.get("summary", {}),
        "status": "complete" if result else "not_found"
    }


@router.get("/ai-analysis/{case_id}")
async def get_cctv_ai_analysis(case_id: str):
    """Run AI agent reasoning on CCTV events for a case."""
    result = _cctv_results.get(case_id, {})
    if not result:
        return {"case_id": case_id, "status": "no_cctv_data"}

    from app.ai.cctv_agent import analyze_cctv
    analysis = analyze_cctv(case_id, result.get("events", []), result.get("flags", []))
    return {"case_id": case_id, "agent": "cctv_agent", "analysis": analysis}


def _run_cctv_pipeline(case_id: str, path: str, video_id: str):
    from app.services.cctv_service import analyze_video, detect_suspicious_activity, get_video_summary
    events = analyze_video(path, case_id)
    flags = detect_suspicious_activity(events)
    summary = get_video_summary(events)
    _cctv_results[case_id] = {"video_id": video_id, "events": events, "flags": flags, "summary": summary}
