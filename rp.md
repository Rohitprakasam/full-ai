# RAW Backend — Complete Reproduction Plan (v2.1)

> Feed this document to any AI coding assistant to reproduce the exact backend.
> This version (v2.1) includes all production-readiness features: Docker healthchecks, streaming copilot, audit logs, MongoDB keyword search, MFA (TOTP), face recognition, and smoke tests.

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
**CCTV**: YOLOv8 + DeepSORT + DeepFace (Face Recognition)
**Voice**: faster-whisper
**Auth**: JWT (passlib bcrypt + python-jose) + TOTP MFA (pyotp)

---

## FOLDER STRUCTURE

```
app/
├── __init__.py                 # empty
├── config.py                   # Settings via pydantic-settings
├── database.py                 # MongoDB init via Beanie (with text indexes)
├── main.py                     # FastAPI app + route registration + middlewares
├── middleware/                 
│   ├── __init__.py             
│   └── audit.py                # Audit log middleware
├── models/
│   ├── __init__.py             # re-exports all models
│   ├── user.py                 # User document (with MFA fields)
│   ├── case.py                 # Case document + AI fields
│   ├── evidence.py             # Evidence document + AI fields
│   ├── timeline.py             # TimelineEvent document
│   └── audit.py                # AuditLog document
├── schemas/
│   ├── __init__.py             # empty
│   ├── user.py                 # UserCreate, UserOut, Token, TokenData, MFA schemas
│   ├── case.py                 # CaseCreate, CaseUpdate, CaseOut
│   └── timeline.py             # TimelineEventCreate, TimelineEventOut
├── utils/
│   ├── __init__.py             # empty
│   ├── security.py             # JWT + bcrypt + get_current_user + get_current_user_from_request
│   └── storage.py              # MinIO client + upload_file
├── routes/
│   ├── __init__.py             # empty
│   ├── auth.py                 # POST register/login/logout + MFA setup/verify + Audit logs
│   ├── cases.py                # CRUD cases
│   ├── upload.py               # Evidence upload → triggers AI pipeline
│   ├── timeline.py             # Timeline CRUD
│   ├── ai_routes.py            # Manual AI trigger + status check
│   ├── copilot.py              # Investigation copilot chat (Streaming + non-streaming)
│   ├── graph.py                # Neo4j graph queries
│   ├── search.py               # Milvus semantic search + MongoDB keyword search
│   ├── agents.py               # AI agent execution (7 agents)
│   ├── cctv.py                 # CCTV upload + analysis + face registration
│   └── voice.py                # Audio transcription
├── services/
│   ├── __init__.py             # empty
│   ├── llm_client.py           # Featherless AI client (chat, embed, tools, streaming)
│   ├── ocr_service.py          # PaddleOCR + PyMuPDF
│   ├── nlp_service.py          # Summarize + NER
│   ├── graph_service.py        # Neo4j CRUD
│   ├── search_service.py       # Milvus embed + search
│   ├── risk_service.py         # Rule-based risk scoring
│   ├── cctv_service.py         # YOLOv8 + DeepSORT + face integration
│   ├── face_service.py         # DeepFace suspect face registration & identification
│   ├── mfa_service.py          # pyotp TOTP + QR code generation
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
tests/
├── conftest.py                 # Shared fixtures (async client, auth)
├── test_auth.py                # Register/login tests
├── test_cases.py               # CRUD case tests
└── test_evidence.py            # Smoke tests for evidence upload pipeline
```

Root files: `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `.env`, `.env.example`, `start.bat`

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
**Text Indexes**: Creates text indexes on `evidence` (`ai_summary`, `ai_raw_text`, `type`) and `cases` (`title`, `crime_type`) for keyword search.

---

## MODELS (5 Beanie Documents)

**User**: name(str), role(str="officer"), email(EmailStr), password_hash(str), mfa_enabled(bool=False), mfa_secret(Optional[str]). Collection: "users"

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
**MFASetupResponse**: secret(str), qr_code(str base64)
**MFAVerifyRequest**: code(str)

---

## UTILS

**security.py**: bcrypt CryptContext, OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login"). Functions: `verify_password`, `get_password_hash`, `create_access_token(subject, expires_delta)` using python-jose, `get_current_user(token)` — decodes JWT, finds User by email, `get_current_user_from_request(request)` — soft version for middleware.

**storage.py**: MinIO client instance. Functions: `ensure_bucket(name)`, `upload_file(bucket, object, data_bytes, content_type)` — creates bucket if missing, uploads via `put_object`.

---

## 36 API ENDPOINTS

### Auth (prefix="/auth")
1. `POST /register` — Create user, hash password, return UserOut
2. `POST /login` — OAuth2 form, verify password (enforces MFA if enabled), return JWT Token
3. `POST /logout` — Requires auth, returns success message
4. `POST /mfa/setup` — Generate TOTP secret and QR code
5. `POST /mfa/verify` — Verify code to enable MFA
6. `POST /mfa/disable` — Disable MFA
7. `GET /audit-logs` — Query recent audit logs

### Cases (prefix="/cases")
8. `POST /` — Create case, requires auth
9. `GET /` — List all cases
10. `GET /{case_id}` — Get single case
11. `PUT /{case_id}` — Update status/risk_score

### Evidence (prefix="/evidence")
12. `POST /upload` — Form: case_id, type, file. SHA256 hash → MinIO upload → save Evidence doc → `process_evidence_task.delay(evidence_id, case_id, type)`
13. `GET /case/{case_id}` — List evidence for case
14. `GET /{evidence_id}` — Get single evidence

### Timeline (prefix="/timeline")
15. `POST /event` — Create timeline event
16. `GET /{case_id}` — Get sorted timeline

### AI Analysis (prefix="/ai")
17. `POST /analyze/evidence` — Body: {evidence_id, case_id}. Triggers Celery task, sets status="processing"
18. `GET /status/{evidence_id}` — Returns ai_status, ai_summary, ai_entities

### Copilot (prefix="/copilot")
19. `POST /ask` — Streaming SSE chat completion. Body: {case_id, question, conversation_history[]}
20. `POST /ask/full` — Non-streaming fallback chat completion.

### Search (prefix="/search")
21. `POST /semantic` — Semantic search on Milvus
22. `GET /keyword` — MongoDB text search across evidence summaries and raw text
23. `GET /cases` — MongoDB text search across cases

### Graph (prefix="/graph")
24. `GET /case/{case_id}` — Full Neo4j graph (nodes+edges)
25. `GET /suspect/{name}` — 3-hop connections from person
26. `GET /mastermind/{case_id}` — Top 5 most-connected persons
27. `POST /add-relationship` — Body: {source_name, source_type, target_name, target_type, relationship}

### Agents (prefix="/agents")
28. `POST /evidence/{case_id}` — Evidence analysis agent
29. `POST /timeline/{case_id}` — Timeline reconstruction agent
30. `POST /legal-report/{case_id}` — Legal report agent
31. `GET /risk/{case_id}` — Calculate risk, save to Case model
32. `POST /autopsy/{case_id}` — Autopsy intelligence agent
33. `POST /graph/{case_id}` — Graph intelligence agent

### CCTV (prefix="/cctv")
34. `POST /analyze/{case_id}` — Upload video, run YOLO+DeepSORT+DeepFace in background
35. `GET /events/{case_id}` — Get detection and face match events
36. `GET /ai-analysis/{case_id}` — CCTV agent reasoning
37. `POST /register-face/{case_id}` — Register a suspect face for DeepFace recognition

### Voice (prefix="/voice")
38. `POST /transcribe/{case_id}` — Upload audio, transcribe, extract entities, summarize

---

## SERVICES

**llm_client.py**: OpenAI client pointing to Featherless. Includes `AsyncOpenAI` for streaming. Functions: `chat_completion`, `stream_chat_completion`, `generate_embeddings`, `generate_embeddings_batch`, `chat_completion_with_tools`.

**ocr_service.py**: PaddleOCR instance. Functions: `extract_text_from_image`, `extract_text_from_pdf` via PyMuPDF.

**nlp_service.py**: spaCy en_core_web_sm. Functions: `summarize_text`, `extract_entities` returns {persons, locations, dates, organizations, money}, `analyze_text_full`.

**graph_service.py**: Neo4j driver. Functions: `add_entities_to_graph` — MERGE nodes, `find_connected_suspects`, `get_full_case_graph`, `detect_mastermind`, `add_relationship`.

**search_service.py**: Milvus. Functions: `init_milvus()`, `store_embedding`, `semantic_search`.

**risk_service.py**: Pure Python rules. `calculate_risk_score(case_data)`. Returns {score, risk_level, flags, recommendation}.

**cctv_service.py**: YOLOv8n + DeepSort. `analyze_video(path, case_id, run_face_recognition=True)` — every 10th frame YOLO, every 30th frame DeepFace. Returns detection_events, face_events, suspicious_activity. `detect_suspicious_activity` flags loitering.

**face_service.py**: DeepFace. `register_suspect_face`, `identify_face_in_frame` (Facenet512 + retinaface).

**mfa_service.py**: pyotp. `generate_mfa_secret`, `generate_qr_code`, `verify_totp`.

**voice_service.py**: WhisperModel("base", cpu, int8). `transcribe_audio`.

**metadata_service.py**: `extract_metadata`. `extract_image_metadata`.

**timeline_service.py**: `merge_timelines`. `detect_timeline_gaps`.

---

## MIDDLEWARES

**audit.py**: `AuditMiddleware` intercepts all POST, PUT, PATCH, DELETE requests on non-skip paths, extracts `user_id` from JWT, and writes an `AuditLog` entry to MongoDB asynchronously.

---

## AI AGENTS (all use agent_runner.py)

**agent_runner.py**: `run_agent(name, system_prompt, context, model)` — wraps `chat_completion`. `run_agent_with_tools` wraps tool execution.

- **evidence_agent**: Analyzes evidence consistency, contradictions, missing evidence
- **timeline_agent**: Reconstructs chronological sequence, identifies gaps
- **cctv_agent**: Identifies suspicious individuals, loitering, anomalies from CCTV events
- **autopsy_agent**: Extracts injuries, toxicology, cause of death from medical reports
- **graph_agent**: Identifies masterminds, hidden relationships, criminal networks
- **legal_report_agent**: Generates structured court-ready report with 7 sections

**tool_registry.py**: 7 OpenAI-format tool definitions (search_evidence, get_suspect_connections, get_timeline_events, calculate_risk_score, get_case_graph, analyze_cctv_events, get_autopsy_analysis).

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

---

## MAIN APP (app/main.py)

FastAPI with lifespan (calls `init_db()` + creates upload dir). CORS middleware + `AuditMiddleware`. Registers 11 routers all prefixed with `/api/v1`. Health check at `/health`. Root `/` lists all endpoints.

---

## DOCKER COMPOSE (8 services + Healthchecks)

1. **db**: mongo:6-jammy (port 27017, healthcheck mongosh ping)
2. **redis**: redis:7-alpine (port 6379, healthcheck redis-cli ping)
3. **minio**: minio/minio (ports 9000, 9001, healthcheck curl live)
4. **neo4j**: neo4j:5 (ports 7474, 7687, healthcheck wget spider)
5. **milvus-etcd**: etcd:v3.5.5 (healthcheck etcdctl)
6. **milvus-minio**: minio for Milvus internal storage
7. **milvus**: milvusdb/milvus:v2.4.0 (port 19530, healthcheck curl healthz)
8. **api**: builds Dockerfile, uvicorn on port 8000. `depends_on` all above with `condition: service_healthy`
9. **worker**: builds same Dockerfile, runs celery worker. `depends_on` db and redis `service_healthy`.

Volumes: mongo_data, minio_data, neo4j_data

---

## TESTS (`/tests/`)

Uses `pytest` and `httpx`.
- `conftest.py`: `event_loop`, `client`, `auth_headers` (registers/logins a test user)
- `test_auth.py`: register, login, login with wrong password
- `test_cases.py`: create case, list cases, get case
- `test_evidence.py`: test evidence upload pipeline and file hash consistency

Run with: `pytest tests/ -v`

---

## DOCKERFILE

Python 3.11-slim. Install libgl1-mesa-glx + libglib2.0-0 (OpenCV deps). pip install requirements. Download spacy en_core_web_sm. CMD uvicorn.

---

## KEY DESIGN DECISIONS

1. MongoDB instead of PostgreSQL — Person 1 built with Beanie ODM. Full Text Search added via MongoDB text indexes (`/search/keyword`).
2. Featherless AI instead of local Ollama — serverless, no GPU needed. Supports SSE streaming for Copilot.
3. Agents are sandboxed — receive only context strings, never direct DB access.
4. Upload route fires Celery task — async AI processing doesn't block HTTP response.
5. Copilot queries MongoDB directly via Beanie — no inter-service HTTP calls. Supports Server-Sent Events (SSE) streaming.
6. Risk scoring is pure Python rules — no LLM needed, instant results.
7. Audit Log Middleware intercepts requests dynamically — avoids rewriting 30 route handlers.
8. MFA TOTP via `pyotp` — provides industry-standard 2FA without complex 3rd party providers.
9. Docker Healthchecks — ensures the API starts only after DBs are ready, preventing race conditions.
