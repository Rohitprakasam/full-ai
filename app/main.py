"""
RAW — AI-Powered Unified Investigation Operating System (v2.1)
All fixes applied: healthchecks, streaming, audit, keyword search, MFA, face recognition.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

from app.routes import auth, cases, upload, timeline
from app.routes import ai_routes, graph, search, copilot, agents, voice, cctv


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Unified Investigation OS — Featherless AI + Neo4j + Milvus + YOLOv8",
    version="2.1.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# FIX 3: Audit middleware
from app.middleware.audit import AuditMiddleware
app.add_middleware(AuditMiddleware)

# Routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(timeline.router, prefix=settings.API_V1_STR)
app.include_router(ai_routes.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(copilot.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(cctv.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok", "service": settings.PROJECT_NAME, "version": "2.1.0",
        "infrastructure": {"database": settings.MONGO_URL, "storage": settings.MINIO_URL, "cache": settings.REDIS_URL},
        "ai_services": {
            "llm_provider": "Featherless AI", "primary_model": settings.LLM_MODEL_PRIMARY,
            "neo4j": settings.NEO4J_URI, "milvus": f"{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
        }
    }


@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "docs": "/docs", "version": "2.1.0"}
