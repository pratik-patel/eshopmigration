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

---

## 8. Code Quality Standards

### 8.1 Python Code Quality

#### Linting & Formatting
- **Ruff** — all-in-one linter (replaces flake8, isort, pyupgrade)
- **Black** — code formatter (line length: 100)
- **mypy** — static type checking (strict mode)

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "A",   # flake8-builtins
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "T10", # flake8-debugger
    "RET", # flake8-return
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by black)
]

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Pre-commit hooks** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, fastapi, sqlalchemy]
```

#### Code Complexity Limits
- **Cyclomatic complexity**: Max 10 per function (enforced by Ruff's `C901`)
- **Function length**: Max 50 lines (excluding docstrings and blank lines)
- **Class length**: Max 300 lines (split into multiple classes if exceeded)
- **File length**: Max 500 lines (split into multiple modules if exceeded)
- **Max arguments per function**: 5 (use Pydantic models for more)

**Docstring Requirements**:
- All public functions, classes, and modules must have docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections

```python
async def get_channel_state(
    channel_id: str,
    service: ChannelService = Depends(get_channel_service),
) -> ChannelStateDto:
    """
    Retrieve current state of a channel.

    Args:
        channel_id: Channel identifier in format PluginId.ChannelName
        service: Injected channel service dependency

    Returns:
        Current channel state with value, type, status, and timestamp

    Raises:
        NotFoundException: If channel does not exist
        ValidationError: If channel_id format is invalid
    """
    return await service.get_state(channel_id)
```

### 8.2 TypeScript/React Code Quality

#### Linting & Formatting
- **ESLint** — linting with TypeScript rules
- **Prettier** — code formatter
- **TypeScript** — strict type checking

**Configuration** (`eslint.config.js`):
```javascript
import js from '@eslint/js';
import typescript from '@typescript-eslint/eslint-plugin';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      '@typescript-eslint': typescript,
      'react': react,
      'react-hooks': reactHooks,
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'complexity': ['error', 10],
      'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],
      'max-params': ['error', 4],
    },
  },
];
```

**Prettier** (`.prettierrc`):
```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2
}
```

**TypeScript** (`tsconfig.json`):
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

#### Component Complexity Limits
- **Component length**: Max 200 lines (split into smaller components)
- **Props per component**: Max 7 (use composition or group into objects)
- **Hook calls per component**: Max 10 (extract to custom hooks)
- **JSX nesting depth**: Max 5 levels (extract to sub-components)

---

## 9. Code Coverage Requirements

### 9.1 Python Backend Coverage

**Minimum thresholds** (enforced in CI):
- **Overall coverage**: 80%
- **New code coverage**: 90%
- **Critical paths** (auth, payment, data validation): 95%

**Tool**: `pytest-cov`

**Configuration** (`pyproject.toml`):
```toml
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
    "*/config.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]

[tool.coverage.html]
directory = "htmlcov"
```

**Running coverage**:
```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Check coverage threshold
pytest --cov=app --cov-fail-under=80
```

**Coverage exemptions**:
- Use `# pragma: no cover` sparingly — only for:
  - Defensive assertions that should never execute
  - Type checking blocks (`if TYPE_CHECKING:`)
  - Abstract methods (already marked with `@abstractmethod`)
  - Debug/development-only code paths

### 9.2 React Frontend Coverage

**Minimum thresholds**:
- **Overall coverage**: 75%
- **Components**: 80%
- **Hooks**: 85%
- **Utils/helpers**: 90%

**Tool**: Vitest with `@vitest/coverage-v8`

**Configuration** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/components/ui/', // shadcn components (external)
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData/*',
      ],
      thresholds: {
        lines: 75,
        functions: 75,
        branches: 70,
        statements: 75,
      },
    },
  },
});
```

**Running coverage**:
```bash
# Run tests with coverage
npm run test:coverage

# Generate HTML report
npm run test:coverage -- --reporter=html
```

### 9.3 Coverage Reporting

**CI Integration**: Coverage reports must be uploaded on every PR

- **Backend**: Upload to Codecov/Coveralls
- **Frontend**: Upload to Codecov/Coveralls
- **PR comments**: Automated bot comments with coverage diff

**Badges**: Add coverage badges to README.md
```markdown
[![Backend Coverage](https://codecov.io/gh/org/repo/branch/main/graph/badge.svg?flag=backend)](https://codecov.io/gh/org/repo)
[![Frontend Coverage](https://codecov.io/gh/org/repo/branch/main/graph/badge.svg?flag=frontend)](https://codecov.io/gh/org/repo)
```

---

## 10. Clean Code Principles

### 10.1 SOLID Principles

#### Single Responsibility Principle (SRP)
- Each class/function does **one thing** and does it well
- If you need "and" to describe what it does, split it

```python
# Bad — multiple responsibilities
class ChannelService:
    def get_channel_and_send_email(self, channel_id: str):
        channel = self.get_channel(channel_id)
        self.send_notification_email(channel)
        return channel

# Good — single responsibility
class ChannelService:
    def get_channel(self, channel_id: str) -> Channel:
        return self.repo.find_by_id(channel_id)

class NotificationService:
    def send_channel_alert(self, channel: Channel):
        self.email_service.send(...)
```

#### Open/Closed Principle (OCP)
- Open for extension, closed for modification
- Use abstract base classes and dependency injection

```python
# Good — extensible without modifying existing code
class PluginBase(ABC):
    @abstractmethod
    async def read_value(self, channel_name: str) -> str:
        pass

class ModbusPlugin(PluginBase):
    async def read_value(self, channel_name: str) -> str:
        # Modbus-specific implementation
        pass

class OPCPlugin(PluginBase):
    async def read_value(self, channel_name: str) -> str:
        # OPC-specific implementation
        pass
```

#### Liskov Substitution Principle (LSP)
- Subtypes must be substitutable for their base types
- Child classes must honor parent contracts

#### Interface Segregation Principle (ISP)
- Many specific interfaces are better than one general-purpose interface
- Don't force clients to depend on methods they don't use

#### Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- Use FastAPI's `Depends()` for all dependencies

### 10.2 DRY (Don't Repeat Yourself)

**Rule**: If you copy-paste code more than once, extract it

```python
# Bad — repeated logic
@router.get("/channels/{id}")
async def get_channel(id: str):
    if not id or "." not in id:
        raise HTTPException(400, "Invalid channel ID")
    # ... logic

@router.put("/channels/{id}")
async def update_channel(id: str, data: ChannelUpdate):
    if not id or "." not in id:
        raise HTTPException(400, "Invalid channel ID")
    # ... logic

# Good — extracted validation
def validate_channel_id(channel_id: str) -> str:
    if not channel_id or "." not in channel_id:
        raise HTTPException(400, "Invalid channel ID format")
    return channel_id

@router.get("/channels/{id}")
async def get_channel(id: str = Depends(validate_channel_id)):
    # ... logic
```

### 10.3 KISS (Keep It Simple, Stupid)

**Rules**:
- Avoid clever code — prefer obvious code
- If it takes more than 30 seconds to understand, simplify
- Don't optimize prematurely — make it work first, then optimize if needed

```python
# Bad — too clever
result = [x for x in (y for y in data if y.status == "Good") if x.value > 10]

# Good — clear and readable
active_channels = [ch for ch in data if ch.status == "Good"]
high_value_channels = [ch for ch in active_channels if ch.value > 10]
```

### 10.4 YAGNI (You Aren't Gonna Need It)

**Rule**: Only implement what you need **right now**

```python
# Bad — over-engineering for hypothetical future
class ChannelService:
    def __init__(self):
        self.cache = RedisCache()  # Not needed yet
        self.queue = MessageQueue()  # Not needed yet
        self.metrics = PrometheusMetrics()  # Not needed yet

# Good — implement when actually needed
class ChannelService:
    def __init__(self, repo: ChannelRepository = Depends(get_repo)):
        self.repo = repo
```

### 10.5 Naming Conventions

**Variables**:
- Use descriptive names — `channel_id`, not `ch_id` or `cid`
- Booleans start with `is_`, `has_`, `can_`, `should_`
- Constants in `UPPER_SNAKE_CASE`

**Functions**:
- Verbs or verb phrases — `get_channel`, `validate_input`, `send_notification`
- Boolean functions start with `is_`, `has_`, `can_`

**Classes**:
- Nouns — `ChannelService`, `PluginManager`, `WebSocketHub`
- Avoid suffixes like `Manager`, `Handler`, `Helper` unless genuinely needed

**Avoid**:
- Single-letter names (except loop counters: `i`, `j`)
- Abbreviations (except well-known: `id`, `url`, `api`)
- Generic names: `data`, `info`, `item`, `obj`, `temp`

### 10.6 Function Design

**Rules**:
- Max 5 parameters (use Pydantic models for more)
- Max 50 lines (excluding docstrings)
- One level of abstraction per function
- No side effects in query functions

```python
# Bad — too many parameters
def create_channel(plugin_id, name, type, unit, min_val, max_val, alarm_high, alarm_low):
    pass

# Good — use a model
def create_channel(config: ChannelConfig):
    pass
```

### 10.7 Error Handling

**Rules**:
- Fail fast — validate at the boundary
- Use specific exceptions, not generic `Exception`
- Never swallow errors silently
- Log errors with context

```python
# Bad
try:
    channel = get_channel(id)
except:
    pass  # Silent failure

# Good
try:
    channel = get_channel(id)
except NotFoundException as e:
    logger.error("channel.not_found", channel_id=id, error=str(e))
    raise HTTPException(404, f"Channel {id} not found")
```

### 10.8 Comments

**Rules**:
- Code should be self-documenting — comments explain **why**, not **what**
- Don't comment bad code — rewrite it
- Keep comments up-to-date with code

```python
# Bad — comment explains what (obvious from code)
# Increment counter by 1
counter += 1

# Good — comment explains why (business context)
# Retain last 1000 readings for compliance audit trail
if len(history) > 1000:
    history = history[-1000:]
```

---

## 11. CI/CD Quality Gates

### 11.1 Pre-commit Checks (Local)

**Python**:
```bash
ruff check . --fix          # Linting with auto-fix
ruff format .               # Code formatting
mypy app/                   # Type checking
pytest --cov=app --cov-fail-under=80  # Tests + coverage
```

**React**:
```bash
npm run lint -- --fix       # ESLint with auto-fix
npm run format              # Prettier
npm run type-check          # TypeScript compilation
npm run test:coverage       # Tests + coverage
```

### 11.2 PR Quality Checklist

**Automated checks** (must pass before merge):
- ✅ All tests pass
- ✅ Code coverage meets threshold (80% backend, 75% frontend)
- ✅ No linting errors
- ✅ No type errors
- ✅ No security vulnerabilities (Snyk/Dependabot)
- ✅ Build succeeds
- ✅ E2E tests pass (critical paths)

**Manual review** (required):
- ✅ Code follows CLAUDE.md conventions
- ✅ Changes are within seam boundaries
- ✅ OpenAPI contract updated (if API changes)
- ✅ Tests cover new functionality
- ✅ No hardcoded secrets or credentials
- ✅ Documentation updated (if needed)

### 11.3 CI Pipeline (GitHub Actions / GitLab CI)

**Stage 1: Quality Checks**
```yaml
quality:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Python Quality
      run: |
        ruff check backend/
        mypy backend/app/
    - name: Frontend Quality
      run: |
        cd frontend
        npm run lint
        npm run type-check
```

**Stage 2: Tests**
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - name: Backend Tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-fail-under=80
    - name: Frontend Tests
      run: |
        cd frontend
        npm run test:coverage
    - name: Upload Coverage
      uses: codecov/codecov-action@v4
      with:
        files: backend/coverage.xml,frontend/coverage/coverage-final.json
        flags: backend,frontend
```

**Stage 3: Build**
```yaml
build:
  runs-on: ubuntu-latest
  steps:
    - name: Build Backend
      run: |
        cd backend
        docker build -t backend:${{ github.sha }} .
    - name: Build Frontend
      run: |
        cd frontend
        npm run build
```

**Stage 4: E2E Tests** (on main branch or tagged releases)
```yaml
e2e:
  runs-on: ubuntu-latest
  needs: [quality, test, build]
  steps:
    - name: Start Services
      run: docker-compose up -d
    - name: Run E2E Tests
      run: |
        cd frontend
        npm run test:e2e
```

### 11.4 Quality Metrics Dashboard

**Track over time**:
- Code coverage trend (backend and frontend)
- Test execution time
- Build success rate
- Linting violations
- Security vulnerabilities
- Tech debt (TODO/FIXME comments, code smells)

**Tools**:
- **SonarQube** — comprehensive code quality analysis
- **Codecov** — coverage tracking and visualization
- **Snyk** — security vulnerability scanning
- **Dependabot** — dependency updates and security alerts

### 11.5 Definition of Done

A seam is **production-ready** only when:

1. ✅ All code quality checks pass
2. ✅ Coverage thresholds met (80% backend, 75% frontend)
3. ✅ Unit tests pass
4. ✅ Integration tests pass
5. ✅ E2E tests pass for critical paths
6. ✅ Security scan shows no critical vulnerabilities
7. ✅ Code review approved by 2+ reviewers
8. ✅ OpenAPI contract validated and versioned
9. ✅ Documentation updated
10. ✅ Evidence file written (`seams/<name>/evidence/evidence.md`)

**Deployment gates**:
- Main branch: Requires all checks + manual approval
- Staging: Automatic on main branch merge
- Production: Manual approval + change management ticket

---

## 12. Security & Best Practices

### 12.1 Security Checklist

**Input Validation**:
- ✅ Validate all user input with Pydantic/Zod
- ✅ Sanitize inputs before using in SQL queries (use ORM, not raw SQL)
- ✅ Reject unexpected content types
- ✅ Enforce input length limits

**Authentication & Authorization**:
- ✅ Use JWT tokens with expiration
- ✅ Store passwords with bcrypt (min 12 rounds)
- ✅ Implement rate limiting on auth endpoints
- ✅ Check authorization on every protected endpoint

**Data Protection**:
- ✅ Never log sensitive data (passwords, tokens, PII)
- ✅ Use environment variables for secrets (never commit to Git)
- ✅ Encrypt sensitive data at rest
- ✅ Use HTTPS only (enforce in production)

**Dependencies**:
- ✅ Keep dependencies up-to-date
- ✅ Run `npm audit` / `pip-audit` regularly
- ✅ Review security advisories from Dependabot/Snyk

### 12.2 OWASP Top 10 Mitigation

| Vulnerability | Mitigation |
|---------------|------------|
| **A01: Broken Access Control** | Check permissions on every endpoint; use FastAPI dependencies |
| **A02: Cryptographic Failures** | Use TLS 1.3; bcrypt for passwords; no hardcoded secrets |
| **A03: Injection** | Use Pydantic/Zod validation; parameterized queries only |
| **A04: Insecure Design** | Threat modeling per seam; security requirements in specs |
| **A05: Security Misconfiguration** | Secure defaults; automated security scans in CI |
| **A06: Vulnerable Components** | Dependabot alerts; `npm audit` / `pip-audit` in CI |
| **A07: Authentication Failures** | JWT with expiration; rate limiting; MFA support |
| **A08: Software/Data Integrity** | Sign releases; verify checksums; SRI for CDN assets |
| **A09: Logging Failures** | Log all auth events; centralized logging; no sensitive data |
| **A10: SSRF** | Validate URLs; allowlist external services; network segmentation |

### 12.3 Performance Best Practices

**Backend**:
- Use connection pooling for DB (SQLAlchemy default)
- Cache frequently accessed data (Redis for distributed cache)
- Use async/await consistently (never block event loop)
- Implement request timeouts (default 30s)
- Add database indexes on foreign keys and query filters

**Frontend**:
- Lazy load routes with React Router
- Use TanStack Query caching (staleTime, cacheTime)
- Debounce search inputs (300ms)
- Paginate large lists (max 100 items per page)
- Optimize images (compress, use WebP, lazy load)

**Monitoring**:
- Track API response times (p50, p95, p99)
- Set up alerts for slow queries (> 1s)
- Monitor WebSocket connection stability
- Track frontend bundle size (keep < 500KB gzipped)

---

## 13. Security Review Process

### 13.1 Pre-Merge Security Review

**Every PR must pass security review** before merge.

#### Automated Security Checks (CI Pipeline)

**Static Analysis**:
```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - name: Bandit (Python Security Linter)
      run: bandit -r backend/app/ -f json -o bandit-report.json

    - name: Safety (Python Dependency Check)
      run: safety check --json

    - name: Snyk (Dependency Vulnerabilities)
      run: snyk test --severity-threshold=high

    - name: ESLint Security Plugin
      run: cd frontend && npm run lint:security

    - name: npm audit
      run: cd frontend && npm audit --audit-level=high
```

**Secret Scanning**:
- **GitGuardian** or **Gitleaks** — detect hardcoded secrets
- Scan for: API keys, passwords, tokens, private keys, connection strings
- Block commits containing secrets

**Configuration** (`.gitleaks.toml`):
```toml
[extend]
useDefault = true

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey)['":\s]*[=:]\s*['"][a-zA-Z0-9]{20,}['"]'''
```

#### Manual Security Review Checklist

**For every PR**, reviewer must verify:

**Input Validation**:
- ✅ All user inputs validated with Pydantic (backend) or Zod (frontend)
- ✅ File uploads have size limits and type restrictions
- ✅ No raw SQL queries (use ORM with parameterized queries)
- ✅ No `eval()`, `exec()`, or code execution from user input

**Authentication & Authorization**:
- ✅ Protected endpoints require valid authentication
- ✅ Authorization checks on resource access (not just authentication)
- ✅ No sensitive operations in GET requests
- ✅ CSRF protection for state-changing operations

**Data Protection**:
- ✅ No secrets in code, logs, or error messages
- ✅ Passwords hashed with bcrypt (never plain text or MD5)
- ✅ PII data encrypted at rest
- ✅ Sensitive data not in URL parameters or query strings

**API Security**:
- ✅ Rate limiting on public endpoints
- ✅ Request size limits enforced
- ✅ CORS configured restrictively (no `*` in production)
- ✅ Security headers configured (CSP, HSTS, X-Frame-Options)

**Frontend Security**:
- ✅ No `dangerouslySetInnerHTML` without sanitization
- ✅ External links use `rel="noopener noreferrer"`
- ✅ No sensitive data in localStorage (use httpOnly cookies)
- ✅ XSS protection via React's default escaping

### 13.2 Security Testing

**Penetration Testing**:
- Run OWASP ZAP or Burp Suite on staging before production
- Test for: SQLi, XSS, CSRF, authentication bypass, privilege escalation

**Dependency Scanning**:
```bash
# Python
pip-audit
safety check

# JavaScript
npm audit
npx better-npm-audit audit
```

**Container Scanning** (if using Docker):
```bash
# Scan Docker images
trivy image backend:latest
docker scout cves backend:latest
```

### 13.3 Security Incident Response

**If a vulnerability is discovered**:

1. **Assess severity** (Critical / High / Medium / Low)
2. **Create private security advisory** on GitHub
3. **Patch immediately** for Critical/High severity
4. **Notify stakeholders** within 24 hours
5. **Document in security.md** (postmortem)

**Security contact**: `security@yourcompany.com`

---

## 14. Accessibility (a11y) Standards

### 14.1 WCAG 2.1 Level AA Compliance

**All UI components must meet WCAG 2.1 Level AA** standards.

#### Keyboard Navigation
- ✅ All interactive elements accessible via keyboard (Tab, Enter, Space)
- ✅ Visible focus indicators (default or custom)
- ✅ Logical tab order (follows visual flow)
- ✅ Skip navigation links for screen readers
- ✅ No keyboard traps

```typescript
// Good — proper keyboard support
export function Dialog({ isOpen, onClose, children }: DialogProps) {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      tabIndex={-1}
    >
      {children}
    </div>
  );
}
```

#### Screen Reader Support
- ✅ All images have `alt` text (empty `alt=""` for decorative images)
- ✅ Form inputs have associated `<label>` or `aria-label`
- ✅ Use semantic HTML (`<nav>`, `<main>`, `<article>`, `<button>`)
- ✅ ARIA attributes where semantic HTML insufficient
- ✅ Dynamic content changes announced (use `aria-live`)

```typescript
// Good — proper labeling
<label htmlFor="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-describedby="email-error"
/>
{error && <div id="email-error" role="alert">{error}</div>}
```

#### Color & Contrast
- ✅ Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text
- ✅ Don't rely solely on color to convey information
- ✅ Focus indicators visible against all backgrounds

**Testing tools**:
```bash
# Automated accessibility testing
npm install --save-dev axe-core @axe-core/react
```

```typescript
// In development mode
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('page has no accessibility violations', async () => {
  const { container } = render(<CatalogListPage />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

#### Forms
- ✅ Clear error messages (not just color)
- ✅ Errors announced to screen readers (`role="alert"`)
- ✅ Required fields marked (`aria-required="true"`)
- ✅ Fieldsets with legends for grouped inputs

#### Interactive Elements
- ✅ Buttons use `<button>` element (not `<div onClick>`)
- ✅ Links for navigation, buttons for actions
- ✅ Disabled state indicated visually and to AT (`aria-disabled="true"`)
- ✅ Loading states announced (`aria-busy="true"`)

### 14.2 Accessibility Checklist (Per Component)

**Before marking component complete**:
- ✅ Keyboard navigable (Tab, Enter, Space, Arrow keys)
- ✅ Screen reader tested (NVDA on Windows, VoiceOver on Mac)
- ✅ Color contrast checked (Chrome DevTools, axe DevTools)
- ✅ Automated a11y tests pass (jest-axe)
- ✅ Semantic HTML used where possible
- ✅ ARIA attributes correct (avoid over-use)
- ✅ Focus management for modals/dialogs
- ✅ Form validation accessible

### 14.3 Testing Tools

**Browser Extensions**:
- **axe DevTools** — automated a11y scanning
- **WAVE** — visual feedback on accessibility issues
- **Lighthouse** — accessibility audit (part of Chrome DevTools)

**Screen Readers**:
- **NVDA** (Windows) — free, most popular
- **JAWS** (Windows) — commercial, industry standard
- **VoiceOver** (Mac/iOS) — built-in

**Manual Testing**:
1. Navigate entire page using only keyboard
2. Enable screen reader and test critical workflows
3. Zoom to 200% and verify layout doesn't break
4. Test in high contrast mode (Windows)

---

## 15. Page Performance Standards

### 15.1 Performance Budgets

**Core Web Vitals** (measured on production):
- **LCP (Largest Contentful Paint)**: < 2.5s (Good)
- **FID (First Input Delay)**: < 100ms (Good)
- **CLS (Cumulative Layout Shift)**: < 0.1 (Good)

**Additional metrics**:
- **TTFB (Time to First Byte)**: < 600ms
- **FCP (First Contentful Paint)**: < 1.8s
- **TTI (Time to Interactive)**: < 3.8s
- **Total Blocking Time**: < 200ms

**Bundle size limits**:
- **Initial JS bundle**: < 200 KB (gzipped)
- **Initial CSS**: < 50 KB (gzipped)
- **Total page weight**: < 1 MB (excluding lazy-loaded content)
- **Images**: < 100 KB each (use compression and WebP)

### 15.2 Frontend Performance Best Practices

#### Code Splitting & Lazy Loading
```typescript
// Route-based code splitting
const CatalogListPage = lazy(() => import('./pages/catalog-list/CatalogListPage'));
const CatalogDetailPage = lazy(() => import('./pages/catalog-detail/CatalogDetailPage'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/catalog" element={<CatalogListPage />} />
        <Route path="/catalog/:id" element={<CatalogDetailPage />} />
      </Routes>
    </Suspense>
  );
}
```

#### Image Optimization
```typescript
// Use next-gen formats with fallback
<picture>
  <source srcSet="/images/product.webp" type="image/webp" />
  <source srcSet="/images/product.jpg" type="image/jpeg" />
  <img
    src="/images/product.jpg"
    alt="Product name"
    loading="lazy"
    width="400"
    height="300"
  />
</picture>
```

**Image requirements**:
- ✅ Compress images (TinyPNG, ImageOptim)
- ✅ Use WebP format with JPEG/PNG fallback
- ✅ Specify width/height to prevent CLS
- ✅ Use `loading="lazy"` for below-fold images
- ✅ Serve responsive images (`srcset`)

#### Bundle Optimization
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
          'query-vendor': ['@tanstack/react-query'],
        },
      },
    },
    chunkSizeWarningLimit: 500, // KB
  },
});
```

#### React Performance
- ✅ Use `React.memo` for expensive components (measured via Profiler)
- ✅ Use `useMemo` for expensive calculations
- ✅ Use `useCallback` for functions passed to memoized children
- ✅ Virtualize long lists (use `react-virtual` for 100+ items)
- ✅ Debounce search inputs (300ms)

```typescript
// Virtualized list for performance
import { useVirtualizer } from '@tanstack/react-virtual';

export function CatalogList({ items }: { items: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div key={virtualRow.index}>
            <ProductCard product={items[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 15.3 Backend Performance Best Practices

#### Database Optimization
```python
# Add indexes for query filters
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    name = Column(String, index=True)  # Indexed for search
    created_at = Column(DateTime, index=True)  # Indexed for sorting

# Use select_related to avoid N+1 queries
async def get_products_with_category(db: AsyncSession):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))  # Eager load
        .limit(100)
    )
    return result.scalars().all()
```

#### Caching Strategy
```python
from functools import lru_cache
from fastapi_cache.decorator import cache

# In-memory cache for expensive computations
@lru_cache(maxsize=128)
def calculate_price(product_id: int, quantity: int) -> Decimal:
    # Expensive calculation
    pass

# Distributed cache for API responses
@router.get("/products")
@cache(expire=300)  # 5 minutes
async def list_products(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Cache entire response for 5 minutes
    return await product_service.list(db, category)
```

#### Async Operations
```python
# Run independent operations concurrently
async def get_dashboard_data(db: AsyncSession):
    # Bad — sequential (slow)
    products = await get_products(db)
    orders = await get_orders(db)
    stats = await get_stats(db)

    # Good — concurrent (fast)
    products, orders, stats = await asyncio.gather(
        get_products(db),
        get_orders(db),
        get_stats(db),
    )

    return DashboardData(products=products, orders=orders, stats=stats)
```

#### API Response Optimization
- ✅ Paginate large result sets (max 100 items per page)
- ✅ Use field filtering (`?fields=id,name,price`)
- ✅ Compress responses (gzip, brotli)
- ✅ Return only required fields (don't over-fetch)
- ✅ Use HTTP caching headers (`ETag`, `Cache-Control`)

```python
from fastapi import Response

@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    product = await product_service.get(db, product_id)

    # Set cache headers
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["ETag"] = f'"{product.updated_at.timestamp()}"'

    return product
```

### 15.4 Performance Testing

#### Lighthouse CI (Frontend)
```yaml
# .github/workflows/performance.yml
lighthouse:
  runs-on: ubuntu-latest
  steps:
    - name: Run Lighthouse CI
      uses: treosh/lighthouse-ci-action@v10
      with:
        urls: |
          http://localhost:5173/
          http://localhost:5173/catalog
        budgetPath: ./lighthouse-budget.json
        uploadArtifacts: true
```

**Budget configuration** (`lighthouse-budget.json`):
```json
{
  "budgets": [
    {
      "path": "/*",
      "timings": [
        { "metric": "interactive", "budget": 3800 },
        { "metric": "first-contentful-paint", "budget": 1800 },
        { "metric": "largest-contentful-paint", "budget": 2500 }
      ],
      "resourceSizes": [
        { "resourceType": "script", "budget": 200 },
        { "resourceType": "stylesheet", "budget": 50 },
        { "resourceType": "image", "budget": 500 },
        { "resourceType": "total", "budget": 1000 }
      ]
    }
  ]
}
```

#### Load Testing (Backend)
```bash
# Install k6 for load testing
k6 run load-test.js
```

**Load test script** (`load-test.js`):
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Less than 1% errors
  },
};

export default function () {
  const res = http.get('http://localhost:8000/api/products');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### 15.5 Performance Monitoring

**Real User Monitoring (RUM)**:
- **Web Vitals** — measure Core Web Vitals in production
- **Sentry Performance** — track frontend performance issues
- **New Relic / Datadog** — full-stack performance monitoring

**Setup Web Vitals reporting**:
```typescript
// src/lib/vitals.ts
import { getCLS, getFID, getLCP } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify(metric),
    keepalive: true,
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
```

**Performance budget alerts**:
- Set up alerts for: LCP > 2.5s, FID > 100ms, CLS > 0.1
- Alert when bundle size exceeds budget (> 200 KB)
- Monitor API response times (p95 > 500ms)

### 15.6 Performance Review Checklist

**Before marking seam complete**:
- ✅ Lighthouse score > 90 (Performance, Accessibility, Best Practices)
- ✅ Core Web Vitals meet "Good" thresholds
- ✅ Bundle size within budget (< 200 KB gzipped)
- ✅ Images optimized (compressed, lazy loaded, WebP)
- ✅ API responses < 500ms (p95)
- ✅ Database queries optimized (indexes, no N+1)
- ✅ Load test passes (100 concurrent users)
- ✅ No performance regressions vs. baseline