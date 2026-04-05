# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack application built with FastAPI (backend) and React (frontend), extending the official [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template). It includes custom organization management features with business units and functions, plus Apache Airflow integration for workflow orchestration.

## Development Commands

### Backend Development
```bash
cd backend
# Install dependencies
uv sync
# Activate virtual environment
source .venv/bin/activate
# Run development server
fastapi dev app/main.py
# Or with uvicorn directly
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
# Install dependencies
bun install
# Run development server (http://localhost:5173)
bun run dev
# Build production version
bun run build
# Generate API client from OpenAPI spec
bun run generate-client
# Run E2E tests
bunx playwright test
# Run E2E tests in UI mode
bunx playwright test --ui
```

### Docker Compose Development
```bash
# Start all services with live reloading
docker compose watch
# Start specific services
docker compose up -d backend
# View logs
docker compose logs backend
# Exec into backend container
docker compose exec backend bash
# Stop specific service (to run locally instead)
docker compose stop frontend
# Clean up everything
docker compose down -v
```

### Testing
```bash
# Run all backend tests (builds, starts, tests, tears down)
bash ./scripts/test.sh
# Run tests against already-running stack
docker compose exec backend pytest
# Run specific test file
docker compose exec backend pytest tests/api/routes/test_items.py
# Run with pytest options (e.g., stop on first failure)
docker compose exec backend pytest -x
# Run tests with coverage
docker compose exec backend pytest --cov=app --cov-report=html
```

### Database Migrations
```bash
# Enter backend container
docker compose exec backend bash
# Create migration after model changes
alembic revision --autogenerate -m "Description of changes"
# Apply migrations
alembic upgrade head
```

### Code Quality
```bash
# Python linting and formatting (runs via pre-commit)
uv run ruff check
uv run ruff format
# Run all pre-commit hooks manually
uv run prek run --all-files
# Frontend linting
bun run lint
```

### API Client Generation
```bash
# Auto-generate frontend client from backend OpenAPI spec
bash ./scripts/generate-client.sh
```

## Architecture

### Backend Structure
- **`app/main.py`**: FastAPI application entry point, includes CORS, Sentry, startup events
- **`app/api/`**: API routes organized by domain (users, items, business_units, functions, files)
- **`app/core/`**: Configuration, security (JWT), database (engine), MinIO client
- **`app/models.py`**: SQLModel models for database tables (User, Item, BusinessUnit, Function, File)
- **`app/crud.py`**: Database operations (CRUD functions) for all models
- **`app/api/deps.py`**: Dependency injection for current user, database session, superuser checks
- **`app/alembic/`**: Database migration versions

**Key Models:**
- `User`: Authentication with JWT, optional relationships to BusinessUnit and Function
- `BusinessUnit`: Organizational unit (business unit hierarchy)
- `Function`: Organizational function/department
- `Item`: Generic example model from template
- `File`: File storage metadata with MinIO integration

**API Route Pattern:**
All routes follow the pattern in `app/api/routes/`:
- GET /resource/ - List items with pagination (skip/limit)
- GET /resource/{id} - Get single item
- POST /resource/ - Create item (superuser only)
- PUT /resource/{id} - Update item (superuser or owner)
- DELETE /resource/{id} - Delete item (superuser only)

### Frontend Structure
- **`src/client/`**: Auto-generated OpenAPI client (do not edit manually)
- **`src/components/`**: Reusable UI components (shadcn/ui + Radix UI)
- **`src/routes/`**: TanStack Router file-based routing with code splitting
- **`src/hooks/`**: Custom React hooks
- **`src/lib/`**: Utility functions, TanStack Query client setup

**State Management:**
- TanStack Query for server state (API calls)
- TanStack Router for routing and route-level state
- React Hook Form + Zod for form validation

**Styling:**
- Tailwind CSS v4 with Vite plugin
- shadcn/ui components (Radix UI primitives + Tailwind)
- Dark mode via next-themes

### Environment Configuration
Multi-environment setup with `.env` files:
- `.env` - Base configuration
- `.env.dev` - Development overrides
- `.env.staging` - Staging environment
- `.env.prod` - Production environment

**Critical Settings (change before deployment):**
- `SECRET_KEY` - JWT signing key
- `FIRST_SUPERUSER_PASSWORD` - Default admin password
- `POSTGRES_PASSWORD` - Database password

Configuration is loaded in `app/core/config.py` using Pydantic Settings. The backend reads from `../.env` (one level above backend directory).

### Services Infrastructure
- **PostgreSQL**: Primary database (port 5432)
- **Redis**: Caching/message queue (port 6379)
- **MinIO**: S3-compatible object storage (port 9000)
- **Adminer**: Database web UI (port 8080)
- **Mailcatcher**: Email testing (port 1080, SMTP 1025)
- **Traefik**: Reverse proxy/load balancer (port 8090)
- **Airflow**: Workflow orchestration (separate compose file)

## Key Patterns

### Adding a New Resource
1. **Backend**: Add model to `app/models.py`
2. **Backend**: Add CRUD functions to `app/crud.py`
3. **Backend**: Create API routes in `app/api/routes/`
4. **Backend**: Register router in `app/api/main.py`
5. **Generate migrations**: `alembic revision --autogenerate -m "..."`
6. **Run migrations**: `alembic upgrade head`
7. **Generate client**: `bash ./scripts/generate-client.sh`
8. **Frontend**: Create route components in `frontend/src/routes/`
9. **Frontend**: Use generated client for API calls

### Authentication Flow
- JWT tokens stored in localStorage
- `CurrentUser` dependency extracts and validates token from Authorization header
- Superuser checks via `get_current_active_superuser` dependency
- All non-public routes require `CurrentUser` dependency

### File Storage with MinIO
- MinIO client initialized in `app/core/minio.py`
- Bucket created on startup if it doesn't exist
- File metadata stored in `File` model, actual files in MinIO
- Use `minio_client.client.put_object()` to upload, `get_object()` to download

### Testing Strategy
- Pytest for backend (unit/integration tests)
- Playwright for frontend E2E tests
- Tests use in-memory database or test database
- Coverage reports generated in `htmlcov/index.html`

### Code Quality Tools
- **Pre-commit hooks**: Prek runs Ruff (Python) and Biome (TypeScript/JS) before commits
- **Ruff**: Python linting and formatting (configured in pyproject.toml)
- **Biome**: Frontend linting and formatting
- **Mypy**: Static type checking for Python (strict mode)

## Development URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
- Adminer (DB): http://localhost:8080
- Mailcatcher: http://localhost:1080
- Traefik UI: http://localhost:8090

## Local Development Workflow
1. Start infrastructure: `docker compose watch`
2. Backend runs with live reload in container
3. Either use frontend in container or stop it and run `bun run dev` locally
4. After backend changes: regenerate API client if models/routes changed
5. After model changes: create and run Alembic migrations
6. Before committing: pre-commit hooks auto-format code

## Troubleshooting
- If backend container exits on syntax error: fix and `docker compose watch`
- If migrations fail: check `app/alembic/versions/` for conflicts
- If frontend client outdated: run `bash ./scripts/generate-client.sh`
- If CORS errors: check `BACKEND_CORS_ORIGINS` in `.env`
- If MinIO fails: check MINIO_ENDPOINT and bucket configuration
