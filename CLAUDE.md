# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InspireEd is a STEM education platform based on constructivist and evidence-based PDCA teaching quality management. It integrates multimodal teaching resources (rich text, executable code, PhET simulations, assessment tools) and supports systematic course design, structured activities, process assessment, and data-driven continuous improvement.

**Dual Cycle Framework:**
- **PDCA Cycle** (Teacher): Plan → Do → Check → Act
- **5E Cycle** (Student): Engage → Explore → Explain → Elaborate → Evaluate

## Common Commands

### Development (Local)

```bash
# Start all services (frontend + backend + database)
./start.sh          # macOS/Linux
start.bat           # Windows

# Stop all services
./stop.sh           # macOS/Linux
stop.bat            # Windows

# Frontend only (Vue3 + Vite)
pnpm dev            # Starts on http://localhost:5173
pnpm build          # Production build
pnpm type-check     # TypeScript type checking
pnpm lint           # ESLint

# Backend only (FastAPI)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
cd backend
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1              # Rollback one migration

# Python code formatting (REQUIRED before commits)
black .            # Format code
black --check .    # Check format without modifying
```

### Docker Deployment

```bash
cd docker
docker-compose up -d     # Start PostgreSQL, Redis, MinIO, Kafka, Zookeeper
docker-compose down      # Stop all services
```

### Testing

```bash
# Backend tests (pytest + pytest-asyncio)
cd backend
pytest                  # Run all tests
pytest -v               # Verbose output
pytest --tb=short       # Shorter error tracebacks

# Frontend tests (Vitest)
cd frontend
npm test                # or vitest run
```

## Architecture Overview

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue3 + TypeScript + Vite + Pinia + TailwindCSS |
| Backend | FastAPI + Python 3.10+ |
| Database | PostgreSQL + TimescaleDB |
| Cache | Redis |
| Storage | MinIO (S3-compatible) |
| Message Queue | Kafka + ClickHouse (log analytics) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| AI | LangChain + DeepSeek |
| Vector Search | FAISS |

### Directory Structure

```
inspireed-platform-main/
├── frontend/                    # Vue3 application
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/              # Page-level components
│   │   ├── services/           # API services
│   │   ├── store/              # Pinia state management
│   │   ├── types/              # TypeScript type definitions
│   │   └── utils/              # Utility functions
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py             # Application entry point
│   │   ├── api/                # API routes (organized by module)
│   │   ├── core/               # Core config (database, CORS, security)
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic
│   ├── alembic/                # Database migrations
│   └── requirements.txt
└── docker/docker-compose.yml   # Service orchestration
```

### Key Architectural Patterns

**API Structure:** Routes are organized by feature module in `backend/app/api/`. Each module typically contains:
- CRUD endpoints
- Business logic delegation to services
- Pydantic schema validation

**Service Layer:** Business logic resides in `backend/app/services/`. Services handle:
- Database operations via ORM models
- External API integrations
- Complex business rules

**Frontend State Management:** Pinia stores in `frontend/src/store/` manage global state. API calls are encapsulated in `frontend/src/services/`.

**Cell-based Content:** Lessons are composed of Cells (`Lesson` → `Cell` relationship). Each Cell can be TEXT, VIDEO, CODE, QA, etc., with configurable content stored as JSON.

**Multimodal Resources:**
- Rich text: TipTap editor
- Code execution: CodeMirror + JupyterLite (browser-side Python)
- Simulations: PhET integration
- Media files: MinIO storage

### Database Schema (Core Entities)

- **Organization:** `Region` → `School` → `Classroom` → `User`
- **Curriculum:** `Subject` → `Course` → `Chapter` → `Lesson` → `Cell`
- **Learning:** `ActivitySubmission`, `PeerReview`, `ClassSession`
- **Projects:** `StudentProject` (5E stages), `ProjectCell`
- **Collaboration:** `SubjectGroup`, `Question`/`Answer`, `SharedLesson`
- **Resources:** `LibraryAsset`, `LibraryAssetVersion`

Models are defined in `backend/app/models/` using SQLAlchemy 2.0 async ORM.

### Configuration

**Backend (`.env`):**
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=inspireed
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

**Frontend (`.env.local`):**
```
VITE_API_BASE_URL=    # Leave empty for auto-detection
VITE_APP_TITLE=InspireEd
```

### Auto LAN Access

The platform automatically detects local network access:
- Frontend detects the access IP and matches the backend API
- Backend uses intelligent CORS configuration to allow LAN IP ranges
- Supports CloudStudio cloud development environment

### Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@inspireed.com | admin123 |
| Teacher | teacher@inspired.com | teacher123 |
| Student | student@inspired.com | student123 |
| Researcher | researcher@inspired.com | researcher123 |

### Service URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
