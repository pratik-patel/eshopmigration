# CLAUDE.md — Code Generation Constitution

This file governs all code written in this migration project.
Read it before writing any Python or React code. These rules are non-negotiable.

---

## 1. Project Context

Application-specific facts (codebase path, DB paths, plugin types, seam candidates) are discovered autonomously by the `legacy-context-fabric` agent and stored in `docs/context-fabric/project-facts.json`. Do not look for a PROJECT_CONTEXT.md file — it does not exist.

This migration applies a **generic legacy application → Python + React** strategy. The approach supports WinForms, WebForms, and other .NET frameworks through framework detection and skill delegation.

### High-Level Migration Target

- **Python backend** — FastAPI, async, REST + WebSocket
- **React frontend** — TypeScript, Vite, component-driven SPA

### Legacy Application Type

Legacy .NET application (WinForms, WPF, WebForms) being migrated to modern web-based architecture (Python backend + React frontend). Framework is auto-detected from codebase and documented in `docs/context-fabric/project-facts.json`.

---

## 2. Contract-First Rule

**No backend endpoint and no frontend API call may be written without a corresponding OpenAPI contract entry.**

- OpenAPI specs live in `openapi/`
- DTOs in Python and TypeScript must be generated from or match the contract exactly
- Contract is the source of truth — if code and contract conflict, fix the code

---

## 3. Seam Boundary Rule

Each seam maps one legacy application workflow to one vertical slice.
**Only touch files inside the active seam's designated paths.**

Do not modify another seam's backend routes, models, or frontend pages unless the migration-planner has explicitly approved a dependency.

---

## 4. Python Backend Rules

### 4.1 Framework & Stack

- **FastAPI** — async first; use `async def` for all route handlers unless genuinely blocking
- **Pydantic v2** — all request/response models; no raw dicts across API boundaries
- **SQLAlchemy 2.x async** — ORM for the archiver DB; use `AsyncSession`
- **asyncpg / aiosqlite** — async DB drivers (SQLite for POC, Postgres-compatible in production)
- **WebSockets via FastAPI** — for real-time channel streaming (replaces WCF duplex + SignalR)
- **Python 3.12+**

### 4.2 Project Layout

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory
│   ├── config.py                # Settings via pydantic-settings
│   ├── dependencies.py          # Shared FastAPI dependencies (DI)
│   │
│   ├── channels/                # Channel management seam
│   │   ├── router.py
│   │   ├── schemas.py           # Pydantic models
│   │   ├── service.py           # Business logic
│   │   └── models.py            # SQLAlchemy models (if persisted)
│   │
│   ├── archiver/                # Historical data seam
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── models.py
│   │
│   ├── plugins/                 # Communication plugin abstraction layer
│   │   ├── base.py              # IChannel / ICommunicationPlug equivalents
│   │   ├── modbus.py
│   │   ├── simulator.py
│   │   └── manager.py           # CommunicationPlugs equivalent
│   │
│   ├── websocket/               # Real-time streaming
│   │   ├── hub.py               # Channel update hub
│   │   └── manager.py           # Connection manager
│   │
│   └── core/
│       ├── logging.py
│       ├── exceptions.py
│       └── db.py                # DB engine / session factory
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── parity/                  # Golden output comparisons
│
├── pyproject.toml
└── alembic/                     # DB migrations (only if schema changes needed post-POC)
```

### 4.3 Dependency Injection

Use FastAPI's `Depends()` system — no singleton globals, no service locator.

```python
# Good
async def get_channel_service(
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> ChannelService:
    return ChannelService(plugin_manager)

@router.get("/channels/{channel_id}")
async def get_channel(
    channel_id: str,
    service: ChannelService = Depends(get_channel_service),
):
    ...
```

The legacy `Env` singleton pattern must **not** be reproduced in Python. Every dependency flows through `Depends()`.

### 4.4 Pydantic Models

- All models use `model_config = ConfigDict(from_attributes=True)`
- Separate request/response models — do not reuse the same Pydantic model for both
- `ChannelId` must always be in `PluginId.ChannelName` format — validate with a custom type or validator
- Status maps to a Python `Enum`: `ChannelStatus.GOOD | BAD | UNKNOWN`

```python
class ChannelId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if "." not in v:
            raise ValueError("ChannelId must be in format PluginId.ChannelName")
        return cls(v)
```

### 4.5 Error Handling

Define a consistent error envelope — match the OpenAPI contract:

```python
class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: dict | None = None
```

Register exception handlers in `main.py`. Never return bare HTTP 500s or unstructured errors.

### 4.6 Async & Threading

- Plugin polling (MODBUS/OPC) runs in `asyncio` background tasks or `ThreadPoolExecutor` for blocking I/O
- Use `asyncio.Queue` for channel update propagation to WebSocket clients
- Never block the event loop — wrap any blocking call in `await asyncio.to_thread(...)`

### 4.7 WebSocket / Real-time Streaming

The legacy system used WCF duplex callbacks and SignalR stubs. Replace with FastAPI WebSockets:

```python
# Pattern: per-connection subscription
@router.websocket("/ws/channels")
async def channel_stream(
    websocket: WebSocket,
    hub: ChannelHub = Depends(get_channel_hub),
):
    await hub.connect(websocket)
    try:
        async for update in hub.subscribe():
            await websocket.send_json(update.model_dump())
    except WebSocketDisconnect:
        hub.disconnect(websocket)
```

### 4.8 Logging

- Use `structlog` with JSON output — every log line must carry `channel_id`, `seam`, `request_id`
- Log level from config, not hardcoded
- Never use `print()` in production code

### 4.9 Configuration

Use `pydantic-settings` with environment variable overrides:

```python
class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./scada.db"
    plugin_scan_dir: str = "./plugins"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = ConfigDict(env_file=".env")
```

Never hardcode connection strings, ports, or paths.

### 4.10 Testing

- **Unit tests** — pytest + pytest-asyncio; mock all external I/O
- **Integration tests** — use `httpx.AsyncClient` with `TestClient(app)`
- **Parity tests** — compare Python API output against legacy golden fixtures stored in `seams/<name>/evidence/`
- Minimum coverage expectation: all route handlers and all service methods

### 4.11 What Must NOT Be Done

- No `global` state or module-level mutable singletons
- No raw `dict` as API return type — always a Pydantic model
- No `requests` library in async code — use `httpx`
- No Windows Registry reads — config lives in env vars or `.env` files
- No COM/ActiveX calls in Python — OPC must go through an abstraction layer (`plugins/opc.py`)
- No schema migrations during POC — the archiver SQLite DB is read-only unless a seam explicitly needs writes

---

## 5. React Frontend Rules

### 5.1 Stack

- **React 18** with **TypeScript** (strict mode)
- **Vite** — build tool
- **React Router v6** — routing; one route per seam
- **TanStack Query (React Query) v5** — server state, caching, polling
- **Zustand** — client-only UI state (not for server data)
- **shadcn/ui + Tailwind CSS** — component library and styling
- **Zod** — runtime schema validation of API responses
- **openapi-typescript** — generate TypeScript types from OpenAPI spec

### 5.2 Project Layout

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx                   # Router root
│   │
│   ├── api/
│   │   ├── client.ts             # Base fetch wrapper
│   │   ├── channels.ts           # Channel API calls
│   │   └── archiver.ts           # History API calls
│   │
│   ├── hooks/
│   │   ├── useChannel.ts         # TanStack Query hooks
│   │   ├── useChannelStream.ts   # WebSocket hook
│   │   └── useArchiverHistory.ts
│   │
│   ├── components/
│   │   ├── ui/                   # shadcn base components (do not modify)
│   │   ├── channels/             # Channel-specific components
│   │   │   ├── ChannelValue.tsx
│   │   │   ├── ChannelStatus.tsx
│   │   │   └── ChannelList.tsx
│   │   └── layout/
│   │       ├── AppShell.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── pages/                    # One folder per seam route
│   │   ├── channels/
│   │   │   └── ChannelsPage.tsx
│   │   ├── archiver/
│   │   │   └── ArchiverPage.tsx
│   │   └── designer/
│   │       └── DesignerPage.tsx
│   │
│   ├── stores/                   # Zustand stores (UI state only)
│   │   └── uiStore.ts
│   │
│   ├── types/                    # Generated + hand-written types
│   │   └── api.d.ts              # Generated from OpenAPI spec
│   │
│   └── lib/
│       ├── utils.ts
│       └── ws.ts                 # WebSocket client wrapper
│
├── tests/
│   ├── unit/                     # Vitest unit tests
│   └── e2e/                      # Playwright tests
│
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 5.3 TypeScript Rules

- `strict: true` in tsconfig — no exceptions
- No `any` — use `unknown` and narrow explicitly
- All API response shapes must be validated with Zod at the boundary
- Types for API responses come from `openapi-typescript` output — do not hand-write what can be generated

```typescript
// Bad
const data: any = await fetch(...).then(r => r.json());

// Good
import { z } from "zod";
import type { components } from "@/types/api";

type ChannelState = components["schemas"]["ChannelStateDto"];

const ChannelStateSchema = z.object({
  channelId: z.string(),
  value: z.string(),
  type: z.string(),
  modifyTime: z.string().datetime(),
  status: z.enum(["Good", "Bad", "Unknown"]),
});
```

### 5.4 Data Fetching

- All server state via TanStack Query — no `useEffect` + `useState` for API calls
- Polling interval for channel values: configurable, default 2s (matching legacy OPC timer)
- WebSocket connection for real-time updates: use a custom `useChannelStream` hook

```typescript
// Real-time channel updates
function useChannelStream(channelIds: string[]) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/channels`);
    ws.onmessage = (event) => {
      const update = ChannelUpdateSchema.parse(JSON.parse(event.data));
      queryClient.setQueryData(["channel", update.channelId], update);
    };
    return () => ws.close();
  }, [channelIds, queryClient]);
}
```

### 5.5 Component Rules

- Components are function components with named exports — no default exports from component files
- Props must be typed with explicit interfaces — no inline object types for props
- UI components in `components/` are pure/presentational — no API calls inside them
- Data fetching happens in page-level components or dedicated hooks
- Use `React.memo` only when there is a measured performance problem

### 5.6 Real-time Display (Channel Values)

The legacy system used WPF bindings and `INotifyPropertyChanged`. In React:

- Channel values live in TanStack Query cache, updated via WebSocket messages
- `ChannelValue` component subscribes to the query cache key `["channel", channelId]`
- Status colors: `Good → green`, `Bad → red`, `Unknown → gray` — defined as Tailwind classes, not inline styles

### 5.7 Routing

One route per seam workflow:

```typescript
// App.tsx
<Routes>
  <Route path="/" element={<AppShell />}>
    <Route index element={<Navigate to="/channels" />} />
    <Route path="channels" element={<ChannelsPage />} />
    <Route path="archiver" element={<ArchiverPage />} />
    <Route path="designer" element={<DesignerPage />} />
  </Route>
</Routes>
```

Route paths must match the seam name in `seams/`.

### 5.8 Error Handling

- All API errors must be caught and displayed — never silently swallow errors
- Use TanStack Query's `onError` and `error` state
- Global error boundary at `AppShell` level

### 5.9 Testing

- **Unit/component tests** — Vitest + React Testing Library
- **E2E tests** — Playwright; cover the happy path of each seam
- Test files co-located with source: `ChannelValue.test.tsx` next to `ChannelValue.tsx`

### 5.10 What Must NOT Be Done

- No class components
- No `useEffect` for data fetching — always TanStack Query
- No inline styles — Tailwind only
- No `any` types
- No direct `window.location` manipulation — use React Router's `useNavigate`
- No business logic in components — extract to hooks or services

---

## 6. Shared Rules (Both Python and React)

### 6.1 Channel ID Format

Always `PluginId.ChannelName` — enforce in both Python validators and Zod schemas.
Examples: `MODBUS.Pump1_Speed`, `SIM.Temperature_01`, `TIMER.Heartbeat`

### 6.2 Channel Status

Canonical values: `Good`, `Bad`, `Unknown` — use these strings in the API contract.
Map from legacy `ChannelStatusFlags` enum (0=Unknown, 1=Good, 2=Bad).

### 6.3 Timestamps

All timestamps in **ISO 8601 UTC**. Python: `datetime` with `timezone.utc`. TypeScript: `string` (ISO), parsed with `new Date()` or a date library.

### 6.4 Naming Conventions

| Layer | Convention |
|-------|-----------|
| Python modules | `snake_case` |
| Python classes | `PascalCase` |
| Python functions/vars | `snake_case` |
| TypeScript files | `camelCase.ts`, `PascalCase.tsx` for components |
| TypeScript types/interfaces | `PascalCase` |
| TypeScript functions/vars | `camelCase` |
| React components | `PascalCase` |
| API routes | `kebab-case` (`/api/channel-history`) |
| Seam folder names | `kebab-case` (`docs/seams/channel-list/`) |

### 6.5 No Cross-Cutting Changes Without Approval

Do not change `backend/app/core/`, `backend/app/plugins/`, or `frontend/src/api/client.ts` as a side effect of a seam. If a seam needs a change to shared infrastructure, note it in the seam's `spec.md` first.

---

## 7. Evidence Gate

A seam is **not complete** until:

1. All backend routes return real data (not mocks)
2. All frontend components display live data
3. Unit tests pass
4. Integration/contract tests pass
5. Parity evidence written to `seams/<name>/evidence/evidence.md`

Do not mark a seam done without the evidence file.