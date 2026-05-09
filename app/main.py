"""
RAW — AI-Powered Unified Investigation Operating System
Combined Backend: Person 1 (Infrastructure) + Person 2 (AI Intelligence)

Person 1: Auth, Cases, Evidence Upload, Timeline, MongoDB, MinIO, Celery
Person 2: OCR/NLP, CCTV Analytics, Graph Intelligence, Semantic Search,
          AI Agents, Investigation Copilot, Risk Scoring, Voice Intelligence
          Powered by Featherless AI (https://featherless.ai)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# --- Person 1 routes ---
from app.routes import auth, cases, upload, timeline

# --- Person 2 AI routes ---
from app.routes import ai_routes, graph, search, copilot, agents, voice, cctv


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Combined backend — Person 1 infrastructure + Person 2 AI intelligence. "
                "Powered by Featherless AI.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Person 1 Routes (prefixed with /api/v1) ===
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(timeline.router, prefix=settings.API_V1_STR)

# === Person 2 AI Routes (prefixed with /api/v1) ===
app.include_router(ai_routes.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(copilot.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(cctv.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    status = {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": "2.0.0",
        "infrastructure": {
            "database": settings.MONGO_URL,
            "storage": settings.MINIO_URL,
            "cache": settings.REDIS_URL,
        },
        "ai_services": {
            "llm_provider": "Featherless AI",
            "primary_model": settings.LLM_MODEL_PRIMARY,
            "embedding_model": settings.LLM_MODEL_EMBEDDING,
            "neo4j": settings.NEO4J_URI,
            "milvus": f"{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
        }
    }
    return status


@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "person1_endpoints": {
            "auth": "/api/v1/auth/register, /api/v1/auth/login",
            "cases": "/api/v1/cases",
            "evidence": "/api/v1/evidence/upload, /api/v1/evidence/case/{case_id}",
            "timeline": "/api/v1/timeline/event, /api/v1/timeline/{case_id}",
        },
        "person2_endpoints": {
            "ai_analysis": "/api/v1/ai/analyze/evidence",
            "copilot": "/api/v1/copilot/ask",
            "search": "/api/v1/search/semantic",
            "graph": "/api/v1/graph/case/{case_id}",
            "agents": "/api/v1/agents/evidence/{case_id}",
            "risk": "/api/v1/agents/risk/{case_id}",
            "voice": "/api/v1/voice/transcribe/{case_id}",
            "cctv": "/api/v1/cctv/analyze/{case_id}",
            "autopsy": "/api/v1/agents/autopsy/{case_id}",
            "graph_agent": "/api/v1/agents/graph/{case_id}",
        }
    }
