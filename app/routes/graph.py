"""Graph Intelligence Routes — Neo4j queries."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/graph", tags=["Graph Intelligence"])


class RelationshipRequest(BaseModel):
    source_name: str
    source_type: str = "Person"
    target_name: str
    target_type: str = "Person"
    relationship: str = "KNOWS"


@router.get("/case/{case_id}")
async def get_case_graph(case_id: str):
    from app.services.graph_service import get_full_case_graph
    return get_full_case_graph(case_id)


@router.get("/suspect/{name}")
async def get_suspect_connections(name: str):
    from app.services.graph_service import find_connected_suspects
    connections = find_connected_suspects(name)
    return {"suspect": name, "connections": connections, "total": len(connections)}


@router.get("/mastermind/{case_id}")
async def get_mastermind(case_id: str):
    from app.services.graph_service import detect_mastermind
    return {"case_id": case_id, "top_suspects": detect_mastermind(case_id)}


@router.post("/add-relationship")
async def add_rel(req: RelationshipRequest):
    from app.services.graph_service import add_relationship
    return add_relationship(req.source_name, req.source_type, req.target_name, req.target_type, req.relationship)
