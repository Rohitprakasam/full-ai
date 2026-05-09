# RAW — AI-Powered Unified Investigation Operating System

> An intelligent forensic ecosystem combining AI reasoning, graph analytics, CCTV intelligence, and evidence correlation into one unified investigation platform.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  FastAPI Backend                 │
├────────────────┬────────────────────────────────┤
│  Infrastructure │  AI Intelligence Layer        │
│  ─────────────  │  ──────────────────────       │
│  JWT Auth       │  Featherless AI (LLM)         │
│  MongoDB/Beanie │  PaddleOCR + spaCy (NLP)      │
│  MinIO Storage  │  Neo4j (Graph DB)             │
│  Celery + Redis │  Milvus (Vector Search)       │
│  Case CRUD      │  YOLOv8 + DeepSORT (CCTV)    │
│  Evidence Mgmt  │  faster-whisper (Voice)       │
│  Timeline       │  OpenClaw AI Agents           │
└────────────────┴────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| Database | MongoDB (Beanie ODM) |
| Storage | MinIO |
| Queue | Redis + Celery |
| LLM | Featherless AI (Qwen3-32B) |
| Embeddings | Qwen3-Embedding-8B |
| OCR | PaddleOCR |
| NLP | spaCy |
| Graph DB | Neo4j |
| Vector Search | Milvus |
| CCTV | YOLOv8 + DeepSORT |
| Voice | faster-whisper |
| Deployment | Docker |

## API Endpoints (30 total)

### Auth
- `POST /api/v1/auth/register` — Register
- `POST /api/v1/auth/login` — Login (JWT)
- `POST /api/v1/auth/logout` — Logout

### Cases
- `POST /api/v1/cases` — Create case
- `GET /api/v1/cases` — List cases
- `GET /api/v1/cases/{id}` — Get case
- `PUT /api/v1/cases/{id}` — Update case

### Evidence
- `POST /api/v1/evidence/upload` — Upload evidence → triggers AI pipeline
- `GET /api/v1/evidence/case/{id}` — List evidence by case
- `GET /api/v1/evidence/{id}` — Get single evidence

### AI Analysis
- `POST /api/v1/ai/analyze/evidence` — Trigger AI analysis
- `GET /api/v1/ai/status/{id}` — Check processing status

### Investigation Copilot
- `POST /api/v1/copilot/ask` — Chat with AI copilot

### Semantic Search
- `POST /api/v1/search/semantic` — Natural language evidence search

### Graph Intelligence
- `GET /api/v1/graph/case/{id}` — Case relationship graph
- `GET /api/v1/graph/suspect/{name}` — Suspect connections
- `GET /api/v1/graph/mastermind/{id}` — Most connected suspects
- `POST /api/v1/graph/add-relationship` — Add relationship

### AI Agents
- `POST /api/v1/agents/evidence/{id}` — Evidence analysis
- `POST /api/v1/agents/timeline/{id}` — Timeline reconstruction
- `POST /api/v1/agents/legal-report/{id}` — Legal report generation
- `GET /api/v1/agents/risk/{id}` — Risk scoring
- `POST /api/v1/agents/autopsy/{id}` — Autopsy analysis
- `POST /api/v1/agents/graph/{id}` — Graph intelligence

### CCTV Analytics
- `POST /api/v1/cctv/analyze/{id}` — Upload & analyze video
- `GET /api/v1/cctv/events/{id}` — Detection events
- `GET /api/v1/cctv/ai-analysis/{id}` — AI analysis

### Voice
- `POST /api/v1/voice/transcribe/{id}` — Transcribe audio

### Timeline
- `POST /api/v1/timeline/event` — Add event
- `GET /api/v1/timeline/{case_id}` — Get timeline

## AI Processing Pipeline

```
Evidence Upload → SHA256 Hash → MinIO Storage
       ↓
  Celery Task Queued
       ↓
  OCR (PaddleOCR) → Raw Text
       ↓
  NLP Summary (Featherless AI)
       ↓
  Entity Extraction (spaCy NER)
       ↓
  Embedding Generation (Qwen3-Embedding-8B)
       ↓
  Store in Milvus (Vector DB)
       ↓
  Populate Neo4j Graph
       ↓
  Save Results → MongoDB
```

## 7 AI Agents

| Agent | Purpose |
|-------|---------|
| Evidence Agent | Analyze evidence consistency and gaps |
| Timeline Agent | Reconstruct chronological event chains |
| CCTV Agent | Surveillance footage reasoning |
| Autopsy Agent | Medical forensic analysis |
| Graph Agent | Relationship network intelligence |
| Legal Agent | Court-ready report generation |
| Copilot | Conversational investigation assistant |

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Install Python dependencies
python -m venv venv
.\venv\Scripts\activate    # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Run API server
uvicorn app.main:app --reload --port 8000

# 4. Run Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info

# API docs: http://localhost:8000/docs
```

## Project Structure

```
app/
├── ai/                    # AI Agents
│   ├── openclaw/          # Agent runtime + tool registry
│   ├── evidence_agent.py
│   ├── timeline_agent.py
│   ├── cctv_agent.py
│   ├── autopsy_agent.py
│   ├── graph_agent.py
│   └── legal_report_agent.py
├── models/                # MongoDB models
├── routes/                # API endpoints (11 files)
├── schemas/               # Pydantic schemas
├── services/              # Business logic (11 files)
├── utils/                 # Auth + Storage helpers
├── workers/               # Celery async tasks
├── config.py
├── database.py
└── main.py
```

## License

MIT
