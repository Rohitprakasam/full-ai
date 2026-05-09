"""
Unified AI Processing Task — Replaces Person 1's dummy task with real AI pipeline.
This is the MAIN INTEGRATION POINT between Person 1 and Person 2.

When Person 1 uploads evidence → this task fires → Person 2's AI pipeline runs →
results are saved back to MongoDB in the evidence document.
"""
from app.workers.celery_app import celery_app
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


def _get_sync_db():
    """Get a synchronous-compatible MongoDB connection for Celery workers."""
    from pymongo import MongoClient
    client = MongoClient(settings.MONGO_URL)
    return client[settings.MONGO_DB]


@celery_app.task(name="app.workers.tasks.process_evidence_task")
def process_evidence_task(evidence_id: str, case_id: str = "", file_type: str = ""):
    """
    REAL AI processing pipeline — replaces Person 1's dummy sleep task.

    Steps:
    1. Fetch evidence file path from MongoDB
    2. Download from MinIO
    3. OCR → extract text
    4. NLP → summarize via Featherless AI
    5. NER → extract entities via spaCy
    6. Embed → generate embeddings via Featherless AI
    7. Store embedding in Milvus
    8. Auto-populate Neo4j graph
    9. Save AI results back to MongoDB evidence document
    """
    from bson import ObjectId

    print(f"[AI PIPELINE] Starting for evidence: {evidence_id}")

    db = _get_sync_db()
    evidence_doc = db.evidence.find_one({"_id": ObjectId(evidence_id)})

    if not evidence_doc:
        print(f"[AI PIPELINE] Evidence {evidence_id} not found in DB")
        return {"status": "error", "message": "Evidence not found"}

    # Mark as processing
    db.evidence.update_one(
        {"_id": ObjectId(evidence_id)},
        {"$set": {"ai_status": "processing"}}
    )

    file_path = evidence_doc.get("path", "")
    evidence_type = file_type or evidence_doc.get("type", "")

    # Step 1: Download from MinIO to temp file
    local_path = _download_from_minio(file_path)
    if not local_path:
        db.evidence.update_one(
            {"_id": ObjectId(evidence_id)},
            {"$set": {"ai_status": "failed", "ai_summary": "Failed to download file from storage"}}
        )
        return {"status": "error", "message": "Failed to download from MinIO"}

    # Step 2: OCR — Extract text
    try:
        from app.services.ocr_service import extract_text
        file_ext = file_path.split(".")[-1] if "." in file_path else evidence_type
        raw_text = extract_text(local_path, file_ext)
    except Exception as e:
        raw_text = ""
        print(f"[AI PIPELINE] OCR failed: {e}")

    if not raw_text:
        db.evidence.update_one(
            {"_id": ObjectId(evidence_id)},
            {"$set": {"ai_status": "complete", "ai_summary": "No text content could be extracted",
                       "ai_raw_text": ""}}
        )
        return {"status": "complete", "message": "No text extracted"}

    # Step 3: NLP — Summarize via Featherless AI
    try:
        from app.services.nlp_service import summarize_text
        summary = summarize_text(raw_text)
    except Exception as e:
        summary = f"Summarization failed: {e}"

    # Step 4: NER — Extract entities via spaCy
    try:
        from app.services.nlp_service import extract_entities
        entities = extract_entities(raw_text)
    except Exception as e:
        entities = {}

    # Step 5: Embedding — Generate via Featherless AI
    try:
        from app.services.llm_client import generate_embeddings
        embedding = generate_embeddings(raw_text[:8000])
    except Exception as e:
        embedding = []

    # Step 6: Store embedding in Milvus
    if embedding:
        try:
            from app.services.search_service import store_embedding
            store_embedding(evidence_id, embedding, {
                "case_id": case_id or str(evidence_doc.get("case_id", "")),
                "summary": summary[:2000]
            })
        except Exception as e:
            print(f"[AI PIPELINE] Milvus storage failed: {e}")

    # Step 7: Auto-populate Neo4j graph
    try:
        from app.services.graph_service import add_entities_to_graph
        add_entities_to_graph(entities, evidence_id, case_id or str(evidence_doc.get("case_id", "")))
    except Exception as e:
        print(f"[AI PIPELINE] Neo4j failed: {e}")

    # Step 8: Save results back to MongoDB
    db.evidence.update_one(
        {"_id": ObjectId(evidence_id)},
        {"$set": {
            "ai_status": "complete",
            "ai_summary": summary,
            "ai_entities": entities,
            "ai_raw_text": raw_text[:10000]  # Store first 10k chars
        }}
    )

    print(f"[AI PIPELINE] Complete for evidence: {evidence_id}")
    print(f"  Summary: {summary[:100]}...")
    print(f"  Entities: {entities}")

    return {"status": "complete", "evidence_id": evidence_id, "summary": summary[:200]}


def _download_from_minio(minio_path: str) -> str:
    """Download a file from MinIO to a local temp path."""
    import os
    import tempfile

    try:
        from app.utils.storage import minio_client

        parts = minio_path.split("/", 1)
        if len(parts) != 2:
            return ""
        bucket_name, object_name = parts

        ext = object_name.split(".")[-1] if "." in object_name else "bin"
        local_path = os.path.join(tempfile.gettempdir(), f"evidence_{object_name.replace('/', '_')}")

        minio_client.fget_object(bucket_name, object_name, local_path)
        return local_path
    except Exception as e:
        print(f"[AI PIPELINE] MinIO download failed: {e}")
        return ""
