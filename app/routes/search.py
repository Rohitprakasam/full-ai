"""Semantic Search Routes."""
from fastapi import APIRouter, Query
from pydantic import BaseModel

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
