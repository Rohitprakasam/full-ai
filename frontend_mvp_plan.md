# RAW — Frontend MVP Plan

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| UI | React + Shadcn/ui + Tailwind CSS |
| State | Zustand |
| HTTP | Axios |
| Charts | Recharts |
| Graph Viz | react-force-graph-2d |
| Video | react-player |
| Auth | JWT (localStorage) |

---

## Pages & Route Map

```
/                       → Landing / Login
/dashboard              → Main dashboard (case overview + stats)
/cases                  → Case list
/cases/[id]             → Case detail (tabs: evidence, timeline, graph, risk)
/cases/[id]/evidence    → Evidence list + upload
/cases/[id]/timeline    → AI timeline visualization
/cases/[id]/graph       → Neo4j relationship graph viewer
/cases/[id]/cctv        → CCTV upload + detection viewer
/cases/[id]/report      → AI legal report generator
/copilot                → Investigation copilot chat
/search                 → Semantic evidence search
/voice                  → Voice transcription tool
/settings               → User profile + settings
```

---

## Backend API Mapping

### Auth (`/api/v1/auth`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Register | POST | `/auth/register` |
| Login | POST | `/auth/login` |
| Logout | POST | `/auth/logout` |

### Cases (`/api/v1/cases`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| List cases | GET | `/cases` |
| Create case | POST | `/cases` |
| View case | GET | `/cases/{id}` |
| Update case | PUT | `/cases/{id}` |

### Evidence (`/api/v1/evidence`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Upload evidence | POST | `/evidence/upload` |
| List by case | GET | `/evidence/case/{id}` |
| Get single | GET | `/evidence/{id}` |

### AI Analysis (`/api/v1/ai`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Trigger AI | POST | `/ai/analyze/evidence` |
| Check status | GET | `/ai/status/{id}` |

### Copilot (`/api/v1/copilot`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Ask question | POST | `/copilot/ask` |

### Search (`/api/v1/search`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Semantic search | POST | `/search/semantic` |

### Graph (`/api/v1/graph`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Case graph | GET | `/graph/case/{id}` |
| Suspect links | GET | `/graph/suspect/{name}` |
| Mastermind | GET | `/graph/mastermind/{id}` |
| Add relation | POST | `/graph/add-relationship` |

### Agents (`/api/v1/agents`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Evidence agent | POST | `/agents/evidence/{id}` |
| Timeline agent | POST | `/agents/timeline/{id}` |
| Legal report | POST | `/agents/legal-report/{id}` |
| Risk score | GET | `/agents/risk/{id}` |
| Autopsy agent | POST | `/agents/autopsy/{id}` |
| Graph agent | POST | `/agents/graph/{id}` |

### CCTV (`/api/v1/cctv`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Upload video | POST | `/cctv/analyze/{id}` |
| Get events | GET | `/cctv/events/{id}` |
| AI analysis | GET | `/cctv/ai-analysis/{id}` |

### Voice (`/api/v1/voice`)
| Frontend Action | Method | Endpoint |
|----------------|--------|----------|
| Transcribe | POST | `/voice/transcribe/{id}` |

---

## Page Components

### 1. Login Page (`/`)
- Email + password form
- JWT stored in localStorage
- Redirect to `/dashboard`

### 2. Dashboard (`/dashboard`)
- **Stats cards**: Total cases, open cases, evidence count, risk alerts
- **Recent cases** table
- **Risk distribution** chart (Recharts pie)
- **Quick actions**: New case, Upload evidence, Open copilot

### 3. Case Detail (`/cases/[id]`)
Tabbed layout:

**Evidence Tab**
- Upload dropzone (images, PDFs, docs)
- Evidence table with AI status badge (pending/processing/complete)
- Click to expand: AI summary, entities, raw text

**Timeline Tab**
- Vertical timeline component
- Color-coded by source (manual, CCTV, NLP)
- "Run Timeline Agent" button → shows AI reconstruction

**Graph Tab**
- Force-directed graph visualization (react-force-graph-2d)
- Nodes: Persons (red), Locations (blue), Orgs (green), Evidence (gray)
- Click node → sidebar with details
- "Detect Mastermind" button

**Risk Tab**
- Risk score gauge (0-100)
- Risk level badge (LOW/MEDIUM/HIGH/CRITICAL)
- Flags list
- Recommendation text

**Report Tab**
- "Generate Legal Report" button
- Formatted markdown report display
- Download as PDF option

### 4. CCTV Page (`/cases/[id]/cctv`)
- Video upload zone
- Processing status indicator
- Detection event list (timestamp, track ID, class)
- Suspicious activity flags
- "Run CCTV Agent" button → AI analysis

### 5. Copilot (`/copilot`)
- Chat interface (messages left/right)
- Case selector dropdown
- Conversation history
- Markdown rendering for AI responses

### 6. Search (`/search`)
- Search bar with semantic query input
- Case filter dropdown
- Results cards with relevance score + summary

### 7. Voice (`/voice`)
- Audio file upload
- Transcription display with timestamps
- Extracted entities sidebar
- AI summary panel

---

## Folder Structure

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 (login)
│   ├── dashboard/page.tsx
│   ├── cases/
│   │   ├── page.tsx             (list)
│   │   └── [id]/
│   │       ├── page.tsx         (detail + tabs)
│   │       └── cctv/page.tsx
│   ├── copilot/page.tsx
│   ├── search/page.tsx
│   ├── voice/page.tsx
│   └── settings/page.tsx
├── components/
│   ├── ui/                      (shadcn)
│   ├── Sidebar.tsx
│   ├── EvidenceTable.tsx
│   ├── TimelineView.tsx
│   ├── GraphViewer.tsx
│   ├── RiskGauge.tsx
│   ├── ChatInterface.tsx
│   ├── CCTVPlayer.tsx
│   └── SearchResults.tsx
├── lib/
│   ├── api.ts                   (axios instance)
│   ├── auth.ts                  (JWT helpers)
│   └── store.ts                 (zustand)
├── package.json
└── tailwind.config.ts
```

---

## Implementation Phases

### Phase 1 — Auth + Layout
- Login/register pages
- Sidebar navigation
- Protected route wrapper
- API client setup

### Phase 2 — Cases + Evidence
- Case list + create
- Case detail with tabs
- Evidence upload + AI status display

### Phase 3 — AI Features
- Copilot chat page
- Semantic search page
- Agent trigger buttons + result display

### Phase 4 — Visualizations
- Graph viewer (react-force-graph)
- Timeline component
- Risk gauge
- CCTV event viewer

### Phase 5 — Polish
- Dark mode theme
- Loading states + animations
- Legal report download
- Voice transcription page
