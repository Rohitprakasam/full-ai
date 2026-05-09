"""CCTV Analytics Routes — Upload, analyze, face registration."""
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import shutil, uuid, os
from app.config import settings

router = APIRouter(prefix="/cctv", tags=["CCTV Analytics"])
_cctv_results = {}


@router.post("/analyze/{case_id}")
async def analyze_cctv(case_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}.mp4")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    background_tasks.add_task(_run_cctv_pipeline, case_id, save_path, video_id)
    return {"status": "processing", "video_id": video_id, "case_id": case_id}


@router.get("/events/{case_id}")
async def get_cctv_events(case_id: str):
    result = _cctv_results.get(case_id, {})
    return {
        "case_id": case_id,
        "events": result.get("events", []),
        "flags": result.get("flags", []),
        "face_matches": result.get("face_events", []),
        "summary": result.get("summary", {}),
        "status": "complete" if result else "not_found"
    }


@router.get("/ai-analysis/{case_id}")
async def get_cctv_ai_analysis(case_id: str):
    result = _cctv_results.get(case_id, {})
    if not result:
        return {"case_id": case_id, "status": "no_cctv_data"}
    from app.ai.cctv_agent import analyze_cctv
    analysis = analyze_cctv(case_id, result.get("events", []), result.get("flags", []))
    return {"case_id": case_id, "agent": "cctv_agent", "analysis": analysis}


@router.post("/register-face/{case_id}")
async def register_suspect_face_route(case_id: str, suspect_name: str, file: UploadFile = File(...)):
    """Upload a suspect's photo to enable face recognition in CCTV footage."""
    from app.services.face_service import register_suspect_face
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.UPLOAD_DIR, f"face_{uuid.uuid4()}.jpg")
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    saved_path = register_suspect_face(suspect_name, temp_path)
    return {"message": f"Face registered for suspect: {suspect_name}", "case_id": case_id, "path": saved_path}


def _run_cctv_pipeline(case_id: str, path: str, video_id: str):
    from app.services.cctv_service import analyze_video, detect_suspicious_activity, get_video_summary
    events = analyze_video(path, case_id)
    flags = detect_suspicious_activity(events)
    summary = get_video_summary(events)
    _cctv_results[case_id] = {"video_id": video_id, "events": events, "flags": flags, "summary": summary}
