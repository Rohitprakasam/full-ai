"""Voice Intelligence Routes."""
from fastapi import APIRouter, UploadFile, File
import shutil, uuid, os
from app.config import settings

router = APIRouter(prefix="/voice", tags=["Voice Intelligence"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/transcribe/{case_id}")
async def transcribe(case_id: str, file: UploadFile = File(...)):
    audio_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1] if file.filename else "wav"
    path = os.path.join(settings.UPLOAD_DIR, f"{audio_id}.{ext}")

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    from app.services.voice_service import transcribe_audio
    from app.services.nlp_service import extract_entities, summarize_text

    result = transcribe_audio(path)
    entities = extract_entities(result["full_transcript"])
    summary = summarize_text(result["full_transcript"], context="witness statement / interrogation")

    return {"audio_id": audio_id, "case_id": case_id, "transcript": result, "entities": entities, "ai_summary": summary}
