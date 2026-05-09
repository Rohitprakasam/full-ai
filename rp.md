# RAW Backend — Complete Reproduction Plan

> Feed this document to any AI coding assistant to reproduce the exact backend.

---

## SYSTEM OVERVIEW

**Name**: RAW — AI-Powered Unified Investigation OS
**Framework**: FastAPI (Python 3.11)
**Database**: MongoDB via Beanie ODM
**Storage**: MinIO (S3-compatible)
**Queue**: Redis + Celery
**LLM**: Featherless AI (OpenAI-compatible API at `https://api.featherless.ai/v1`)
**Graph DB**: Neo4j
**Vector DB**: Milvus
**OCR**: PaddleOCR
**NLP**: spaCy (en_core_web_sm)
**CCTV**: YOLOv8 + DeepSORT
**Voice**: faster-whisper
**Auth**: JWT (passlib bcrypt + python-jose)

---

## FOLDER STRUCTURE

```
app/
├── __init__.py                 # empty
├── config.py                   # Settings via pydantic-settings
├── database.py                 # MongoDB init via Beanie
├── main.py                     # FastAPI app + route registration
├── models/
│   ├── __init__.py             # re-exports all models
│   ├── user.py                 # User document
│   ├── case.py                 # Case document + AI fields
│   ├── evidence.py             # Evidence document + AI fields
│   ├── timeline.py             # TimelineEvent document
│   └── audit.py                # AuditLog document
├── schemas/
│   ├── __init__.py             # empty
│   ├── user.py                 # UserCreate, UserOut, Token, TokenData
│   ├── case.py                 # CaseCreate, CaseUpdate, CaseOut
│   └── timeline.py             # TimelineEventCreate, TimelineEventOut
├── utils/
│   ├── __init__.py             # empty
│   ├── security.py             # JWT + bcrypt + get_current_user
│   └── storage.py              # MinIO client + upload_file
├── routes/
│   ├── __init__.py             # empty
│   ├── auth.py                 # POST register/login/logout
│   ├── cases.py                # CRUD cases
│   ├── upload.py               # Evidence upload → triggers AI pipeline
│   ├── timeline.py             # Timeline CRUD
│   ├── ai_routes.py            # Manual AI trigger + status check
│   ├── copilot.py              # Investigation copilot chat
│   ├── graph.py                # Neo4j graph queries
│   ├── search.py               # Milvus semantic search
│   ├── agents.py               # AI agent execution (7 agents)
│   ├── cctv.py                 # CCTV upload + analysis
│   └── voice.py                # Audio transcription
├── services/
│   ├── __init__.py             # empty
│   ├── llm_client.py           # Featherless AI client (chat, embed, tools)
│   ├── ocr_service.py          # PaddleOCR + PyMuPDF
│   ├── nlp_service.py          # Summarize + NER
│   ├── graph_service.py        # Neo4j CRUD
│   ├── search_service.py       # Milvus embed + search
│   ├── risk_service.py         # Rule-based risk scoring
│   ├── cctv_service.py         # YOLOv8 + DeepSORT
│   ├── voice_service.py        # faster-whisper
│   ├── metadata_service.py     # File metadata extraction
│   └── timeline_service.py     # Timeline merge + gap detection
├── ai/
│   ├── __init__.py             # empty
│   ├── openclaw/
│   │   ├── __init__.py         # empty
│   │   ├── agent_runner.py     # Generic agent executor
│   │   └── tool_registry.py    # 7 tool definitions for function calling
│   ├── evidence_agent.py
│   ├── timeline_agent.py
│   ├── cctv_agent.py
│   ├── autopsy_agent.py
│   ├── graph_agent.py
│   └── legal_report_agent.py
└── workers/
    ├── __init__.py             # empty
    ├── celery_app.py           # Celery config
    └── tasks.py                # AI pipeline task (the main integration)
```

Root files: `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `.env`, `start.bat`

---

## CONFIG (app/config.py)

Pydantic BaseSettings with `.env` file support. Fields:
- `PROJECT_NAME` = "RAW — AI-Powered Unified Investigation OS"
- `API_V1_STR` = "/api/v1"
- MongoDB: `MONGO_URL`, `MONGO_DB` = "investigation_os"
- MinIO: `MINIO_URL`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_SECURE=False`
- Redis: `REDIS_URL`
- JWT: `SECRET_KEY`, `ALGORITHM="HS256"`, `ACCESS_TOKEN_EXPIRE_MINUTES=10080` (7 days)
- Featherless: `FEATHERLESS_API_KEY`, `FEATHERLESS_BASE_URL`
- LLM Models: `LLM_MODEL_PRIMARY="Qwen/Qwen3-32B"`, `LLM_MODEL_FAST="Qwen/Qwen2.5-7B-Instruct"`, `LLM_MODEL_EMBEDDING="Qwen/Qwen3-Embedding-8B"`, `LLM_MODEL_AGENT="NousResearch/Hermes-3-Llama-3.1-8B"`
- Neo4j: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- Milvus: `MILVUS_HOST`, `MILVUS_PORT=19530`
- `UPLOAD_DIR="./uploads"`

Export `settings = Settings()` and `MODELS` dict mapping "primary"/"fast"/"embedding"/"agent".

---

## DATABASE (app/database.py)

`init_db()`: Connect via `AsyncIOMotorClient(MONGO_URL)`, then `init_beanie(database, document_models=[User, Case, Evidence, TimelineEvent, AuditLog])`.

---

## MODELS (5 Beanie Documents)

**User**: name(str), role(str="officer"), email(EmailStr), password_hash(str). Collection: "users"

**Case**: title(str), crime_type(str), status(str="open"), risk_score(int=0), created_at(datetime). AI fields: ai_risk_level(Optional[str]), ai_risk_flags(Optional[List[str]]), ai_risk_recommendation(Optional[str]). Collection: "cases"

**Evidence**: case_id(PydanticObjectId), type(str), hash(Optional[str]), path(str), uploaded_by(PydanticObjectId), timestamp(datetime). AI fields: ai_summary(Optional[str]), ai_entities(Optional[Dict]), ai_raw_text(Optional[str]), ai_status(str="pending"). Collection: "evidence"

**TimelineEvent**: case_id(PydanticObjectId), timestamp(datetime), event_type(str), confidence_score(float=1.0), description(Optional[str]). Collection: "timeline_events"

**AuditLog**: user_id(PydanticObjectId), action(str), resource(Optional[str]), timestamp(datetime). Collection: "audit_logs"

---

## SCHEMAS

**UserCreate**: name, email(EmailStr), password, role="officer"
**UserOut**: id, name, email, role
**Token**: access_token, token_type
**CaseCreate**: title, crime_type
**CaseUpdate**: status(Optional), risk_score(Optional)
**CaseOut**: id, title, crime_type, status, risk_score, created_at
**TimelineEventCreate**: case_id(str), event_type, confidence_score=1.0, description(Optional)
**TimelineEventOut**: id, case_id, timestamp, event_type, confidence_score, description

---

## UTILS

**security.py**: bcrypt CryptContext, OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login"). Functions: `verify_password`, `get_password_hash`, `create_access_token(subject, expires_delta)` using python-jose, `get_current_user(token)` — decodes JWT, finds User by email.

**storage.py**: MinIO client instance. Functions: `ensure_bucket(name)`, `upload_file(bucket, object, data_bytes, content_type)` — creates bucket if missing, uploads via `put_object`.

---

## 30 API ENDPOINTS

### Auth (prefix="/auth")
1. `POST /register` — Create user, hash password, return UserOut
2. `POST /login` — OAuth2 form, verify password, return JWT Token
3. `POST /logout` — Requires auth, returns success message

### Cases (prefix="/cases")
4. `POST /` — Create case, requires auth
5. `GET /` — List all cases
6. `GET /{case_id}` — Get single case
7. `PUT /{case_id}` — Update status/risk_score

### Evidence (prefix="/evidence")
8. `POST /upload` — Form: case_id, type, file. SHA256 hash → MinIO upload → save Evidence doc → `process_evidence_task.delay(evidence_id, case_id, type)`
9. `GET /case/{case_id}` — List evidence for case
10. `GET /{evidence_id}` — Get single evidence

### Timeline (prefix="/timeline")
11. `POST /event` — Create timeline event
12. `GET /{case_id}` — Get sorted timeline

### AI Analysis (prefix="/ai")
13. `POST /analyze/evidence` — Body: {evidence_id, case_id}. Triggers Celery task, sets status="processing"
14. `GET /status/{evidence_id}` — Returns ai_status, ai_summary, ai_entities

### Copilot (prefix="/copilot")
15. `POST /ask` — Body: {case_id, question, conversation_history[]}. Builds context from MongoDB (case+evidence+timeline), sends to Featherless AI with system prompt, returns answer

### Search (prefix="/search")
16. `POST /semantic` — Body: {query, case_id?, top_k=5}. Embeds query via Featherless, searches Milvus

### Graph (prefix="/graph")
17. `GET /case/{case_id}` — Full Neo4j graph (nodes+edges)
18. `GET /suspect/{name}` — 3-hop connections from person
19. `GET /mastermind/{case_id}` — Top 5 most-connected persons
20. `POST /add-relationship` — Body: {source_name, source_type, target_name, target_type, relationship}

### Agents (prefix="/agents")
21. `POST /evidence/{case_id}` — Evidence analysis agent
22. `POST /timeline/{case_id}` — Timeline reconstruction agent
23. `POST /legal-report/{case_id}` — Legal report agent
24. `GET /risk/{case_id}` — Calculate risk, save to Case model
25. `POST /autopsy/{case_id}` — Autopsy intelligence agent
26. `POST /graph/{case_id}` — Graph intelligence agent

### CCTV (prefix="/cctv")
27. `POST /analyze/{case_id}` — Upload video, run YOLO+DeepSORT in background
28. `GET /events/{case_id}` — Get detection events
29. `GET /ai-analysis/{case_id}` — CCTV agent reasoning

### Voice (prefix="/voice")
30. `POST /transcribe/{case_id}` — Upload audio, transcribe, extract entities, summarize

---

## SERVICES

**llm_client.py**: OpenAI client pointing to Featherless. Functions: `chat_completion(messages, model, temp=0.3, max_tokens=2048)`, `generate_embeddings(text)`, `generate_embeddings_batch(texts)`, `chat_completion_with_tools(messages, tools, model)`

**ocr_service.py**: PaddleOCR instance. Functions: `extract_text_from_image(path)`, `extract_text_from_pdf(path)` via PyMuPDF, `extract_text(path, file_type)` dispatcher.

**nlp_service.py**: spaCy en_core_web_sm. Functions: `summarize_text(text, context)` via LLM, `extract_entities(text)` returns {persons, locations, dates, organizations, money}, `analyze_text_full(text)` returns {summary, entities, embedding}.

**graph_service.py**: Neo4j driver. Functions: `add_entities_to_graph(entities, evidence_id, case_id)` — MERGE Person/Location/Org nodes linked to Evidence/Case, `find_connected_suspects(name)` — 3-hop query, `get_full_case_graph(case_id)` — returns {nodes, edges}, `detect_mastermind(case_id)` — top 5 by connection count, `add_relationship(source, stype, target, ttype, rel)`.

**search_service.py**: Milvus collection "evidence_embeddings" with fields: id(auto), evidence_id(VARCHAR), case_id(VARCHAR), summary(VARCHAR), embedding(FLOAT_VECTOR dim=4096). IVF_FLAT index, COSINE metric. Functions: `init_milvus()`, `store_embedding(evidence_id, embedding, metadata)`, `semantic_search(query, case_id, top_k)`.

**risk_service.py**: Pure Python. `calculate_risk_score(case_data)` — scores based on evidence volume (+15), suspect count (+20), financial keywords (+10), violence keywords (+25). Returns {score, risk_level, flags, recommendation}.

**cctv_service.py**: YOLOv8n + DeepSort. `analyze_video(path, case_id)` — every 10th frame, detect+track, return events. `detect_suspicious_activity(events)` — flag loitering (>20 appearances). `get_video_summary(events)`.

**voice_service.py**: WhisperModel("base", cpu, int8). `transcribe_audio(path)` — returns {full_transcript, language, duration, segments[]}.

**metadata_service.py**: `extract_metadata(path)` — size, SHA256, MD5, timestamps, mime. `extract_image_metadata(path)` — EXIF via Pillow.

**timeline_service.py**: `merge_timelines(cctv_events, db_events, nlp_dates)` — unifies sources, sorts. `detect_timeline_gaps(events, threshold=3600)`.

---

## AI AGENTS (all use agent_runner.py)

**agent_runner.py**: `run_agent(name, system_prompt, context, model)` — wraps `chat_completion`. `run_agent_with_tools(name, prompt, context, tools)` — wraps `chat_completion_with_tools`.

Each agent has a forensic system prompt and a function that builds context from data, then calls `run_agent()`:

- **evidence_agent**: Analyzes evidence consistency, contradictions, missing evidence
- **timeline_agent**: Reconstructs chronological sequence, identifies gaps
- **cctv_agent**: Identifies suspicious individuals, loitering, anomalies from CCTV events
- **autopsy_agent**: Extracts injuries, toxicology, cause of death from medical reports
- **graph_agent**: Identifies masterminds, hidden relationships, criminal networks
- **legal_report_agent**: Generates structured court-ready report with 7 sections

**tool_registry.py**: 7 OpenAI-format tool definitions: search_evidence, get_suspect_connections, get_timeline_events, calculate_risk_score, get_case_graph, analyze_cctv_events, get_autopsy_analysis.

---

## CELERY WORKER (workers/tasks.py)

**process_evidence_task** — The core integration pipeline:
1. Fetch evidence doc from MongoDB (using pymongo sync driver)
2. Set ai_status="processing"
3. Download file from MinIO to temp dir
4. OCR extract text (ocr_service)
5. NLP summarize via Featherless (nlp_service)
6. NER extract entities via spaCy (nlp_service)
7. Generate embedding via Featherless (llm_client)
8. Store embedding in Milvus (search_service)
9. Populate Neo4j graph with entities (graph_service)
10. Save ai_summary, ai_entities, ai_raw_text, ai_status="complete" back to MongoDB

Uses `pymongo.MongoClient` (sync) since Celery workers can't use async.

---

## MAIN APP (app/main.py)

FastAPI with lifespan (calls `init_db()` + creates upload dir). CORS middleware allows all origins. Registers 11 routers all prefixed with `/api/v1`. Health check at `/health`. Root `/` lists all endpoints.

---

## DOCKER COMPOSE (8 services)

1. **db**: mongo:6-jammy (port 27017)
2. **redis**: redis:7-alpine (port 6379)
3. **minio**: minio/minio (ports 9000, 9001)
4. **neo4j**: neo4j:5 (ports 7474, 7687, auth: neo4j/investigation123)
5. **milvus-etcd**: etcd:v3.5.5
6. **milvus-minio**: minio for Milvus internal storage
7. **milvus**: milvusdb/milvus:v2.4.0 (port 19530)
8. **api**: builds Dockerfile, uvicorn on port 8000
9. **worker**: builds same Dockerfile, runs celery worker

Volumes: mongo_data, minio_data, neo4j_data

---

## DOCKERFILE

Python 3.11-slim. Install libgl1-mesa-glx + libglib2.0-0 (OpenCV deps). pip install requirements. Download spacy en_core_web_sm. CMD uvicorn.

---

## KEY DESIGN DECISIONS

1. MongoDB instead of PostgreSQL — Person 1 built with Beanie ODM
2. Featherless AI instead of local Ollama — serverless, no GPU needed
3. Agents are sandboxed — receive only context strings, never direct DB access
4. Upload route fires Celery task — async AI processing doesn't block HTTP response
5. Copilot queries MongoDB directly via Beanie — no inter-service HTTP calls
6. Risk scoring is pure Python rules — no LLM needed, instant results
