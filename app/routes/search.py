"""Search Routes — Semantic (Milvus) + Keyword (MongoDB FTS)."""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/search", tags=["Search"])


class SemanticSearchRequest(BaseModel):
    query: str
    case_id: str = None
    top_k: int = 5


@router.post("/semantic")
async def search_semantic(req: SemanticSearchRequest):
    from app.services.search_service import semantic_search
    results = semantic_search(req.query, req.case_id, req.top_k)
    return {"query": req.query, "results": results, "total": len(results)}


@router.get("/keyword")
async def search_keyword(
    q: str = Query(..., description="Search term"),
    case_id: str = Query(None, description="Filter by case")
):
    """MongoDB full-text search across evidence summaries and raw text."""
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson import ObjectId
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]

    filter_query = {"$text": {"$search": q}}
    if case_id:
        filter_query["case_id"] = ObjectId(case_id)

    cursor = db["evidence"].find(
        filter_query,
        {"score": {"$meta": "textScore"}, "ai_summary": 1, "type": 1, "case_id": 1}
    ).sort([("score", {"$meta": "textScore"})]).limit(20)

    results = []
    async for doc in cursor:
        results.append({
            "evidence_id": str(doc["_id"]),
            "case_id": str(doc.get("case_id", "")),
            "type": doc.get("type", ""),
            "summary": doc.get("ai_summary", ""),
            "relevance_score": round(doc.get("score", 0), 3)
        })
    return {"results": results, "query": q, "total": len(results)}


@router.get("/cases")
async def search_cases(q: str = Query(...)):
    """Keyword search across case titles and crime types."""
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]

    cursor = db["cases"].find(
        {"$text": {"$search": q}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(10)

    results = []
    async for doc in cursor:
        results.append({
            "case_id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "crime_type": doc.get("crime_type", ""),
            "status": doc.get("status", ""),
        })
    return {"results": results}
