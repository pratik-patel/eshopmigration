---
# Loaded when scaffolding or working in these paths
paths:
  - "backend/**"
  - "frontend/**"
  - ".github/workflows/**"
  - "docker-compose.yml"
---

# Architecture scaffold rules

These rules define the **canonical skeleton** this repo should generate for the selected target architecture.
The `architecture-bootstrap` agent must follow these rules and must not embed the file tree or dependency lists in its own prompt.

## Target architecture selection

The desired stack is configured in:
- `docs/architecture/target-architecture.yml`

If the file is missing, default to:
- **backend:** `fastapi`
- **frontend:** `react_vite`
- **db:** `sqlite`
- **api:** `openapi_rest`
- **websocket:** `true`
- **auth:** `none`

If an unsupported stack is requested, stop and write a blocker file (do not scaffold partially).

## Global scaffolding constraints

- Do not scaffold if `backend/` or `frontend/` already exist.
- Do not write ad-hoc markdown files to repo root.
- Do not hardcode secrets or absolute host paths.
- Keep scaffolding changes confined to:
  - `backend/**`
  - `frontend/**`
  - `.github/workflows/**`
  - `docker-compose.yml`
  - `.env.example` files within backend/frontend

## Stack: fastapi (backend)

### Purpose
Provide a runnable FastAPI service with:
- `/health` endpoint
- OpenAPI enabled by default
- env-var based configuration
- async DB access
- structured logging
- minimal plugin simulator so demos are not empty
- tests that prove boot + health + simulator shape

### Backend folder structure
```text
backend/
├── pyproject.toml
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── core/
│   │   ├── db.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── plugins/
│   │   ├── base.py
│   │   ├── simulator.py
│   │   └── manager.py
│   └── websocket/
│       ├── hub.py
│       └── manager.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── parity/
└── .env.example
```

### Backend dependencies (Poetry)
Required runtime dependencies:
- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `sqlalchemy[asyncio]`
- `aiosqlite` (when db=sqlite)
- `structlog`
- `httpx` (for test client or future adapters)

Required dev dependencies:
- `pytest`
- `pytest-asyncio`
- `ruff`
- `mypy`

### Backend configuration rules
- Configuration MUST be via env vars (no hardcoded local paths):
  - `DB_URL`
  - `LOG_LEVEL`
  - `CORS_ORIGINS`
- Default DB_URL for sqlite in container should point to a container path:
  - `sqlite+aiosqlite:////data/app.db`

### Backend simulator rules
- `SimulatorPlugin` must produce **at least 2** fake channels so websocket/demo is not empty.

### Backend verification commands
The scaffold is considered valid only if all of these pass:
- `poetry run ruff check .`
- `poetry run mypy .`
- `poetry run pytest`

## Stack: react_vite (frontend)

### Purpose
Provide a runnable React/Vite app with:
- Router + simple layout shell
- API client reading base URL from env
- placeholder types file (to be replaced by openapi types generation per seam)
- basic lint + typecheck + test setup

### Frontend folder structure
```text
frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   └── client.ts
│   ├── components/
│   │   └── layout/
│   │       ├── AppShell.tsx
│   │       └── Sidebar.tsx
│   ├── pages/
│   │   └── Home.tsx
│   ├── types/
│   │   └── api.d.ts
│   └── lib/
│       └── utils.ts
└── tests/
    ├── unit/
    └── e2e/
```

### Frontend dependencies
Required runtime dependencies:
- `react`, `react-dom`
- `react-router-dom`
- `@tanstack/react-query`
- `zustand`
- `zod`

Required dev dependencies:
- `vite`
- `typescript`
- `vitest`
- `eslint` (and minimal config)
- `playwright` (optional if e2e is configured)

### Frontend configuration rules
- API base URL reads from `VITE_API_URL`
- `vite.config.ts` should include proxy rules for common local dev:
  - `/api` → backend
  - `/ws` → backend websocket

### Frontend verification commands
- `npm ci`
- `npm run lint`
- `npm run type-check`
- `npm run test` (vitest)

## docker-compose rules (sqlite default)

- Use a **named volume** (no host path bind mount) for sqlite persistence.
- Mount volume at `/data` in the backend container.
- Set `DB_URL` to `sqlite+aiosqlite:////data/app.db` (or equivalent) via env.

## CI workflow rules

Create:
- `.github/workflows/backend.yml` running:
  - poetry install
  - ruff
  - mypy
  - pytest
- `.github/workflows/frontend.yml` running:
  - npm ci
  - lint
  - type-check
  - unit tests
