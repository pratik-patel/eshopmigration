# Python Backend Code Generation Rules

Apply these rules when generating any Python backend code for this migration project.

## Framework & Stack

- **FastAPI** — async first; use `async def` for all route handlers unless genuinely blocking
- **Pydantic v2** — all request/response models; no raw dicts across API boundaries
- **SQLAlchemy 2.x async** — ORM for the archiver DB; use `AsyncSession`
- **asyncpg / aiosqlite** — async DB drivers (SQLite for POC, Postgres-compatible in production)
- **WebSockets via FastAPI** — for real-time channel streaming
- **Python 3.12+**

## Project Structure Convention

```
backend/
├── app/
│   ├── main.py                  # FastAPI app factory
│   ├── config.py                # Settings via pydantic-settings
│   ├── dependencies.py          # Shared FastAPI dependencies (DI)
│   │
│   ├── {seam}/                  # Per-seam vertical slice
│   │   ├── router.py
│   │   ├── schemas.py           # Pydantic models
│   │   ├── service.py           # Business logic
│   │   └── models.py            # SQLAlchemy models (if persisted)
│   │
│   ├── plugins/                 # Communication plugin abstraction layer
│   ├── websocket/               # Real-time streaming
│   └── core/
│       ├── logging.py
│       ├── exceptions.py
│       └── db.py
├── tests/{unit,integration,parity}/
└── pyproject.toml
```

## Dependency Injection

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

**Never** reproduce the legacy `Env` singleton pattern. Every dependency flows through `Depends()`.

## Pydantic Models

- All models use `model_config = ConfigDict(from_attributes=True)`
- Separate request/response models — do not reuse the same Pydantic model for both
- `ChannelId` must always be in `PluginId.ChannelName` format — validate with pattern
- Status maps to Python `Enum`: `ChannelStatus.GOOD | BAD | UNKNOWN`

```python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

class ChannelStatus(str, Enum):
    GOOD = "Good"
    BAD = "Bad"
    UNKNOWN = "Unknown"

class ChannelStateDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel_id: str = Field(..., pattern=r'^[A-Z_]+\.[A-Za-z0-9_]+$')
    value: str
    type: str
    status: ChannelStatus
    modify_time: datetime  # Always UTC
```

## Error Handling

Define consistent error envelope:

```python
class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: dict | None = None

class NotFoundException(HTTPException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id '{identifier}' not found"
        )
```

Register exception handlers in `main.py`. Never return bare HTTP 500s or unstructured errors.

## Async & Threading

- Plugin polling (MODBUS/OPC) runs in `asyncio` background tasks or `ThreadPoolExecutor` for blocking I/O
- Use `asyncio.Queue` for channel update propagation to WebSocket clients
- **Never block the event loop** — wrap any blocking call in `await asyncio.to_thread(...)`

## WebSocket / Real-time Streaming

```python
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

## Logging

- Use `structlog` with JSON output
- Every log line must carry `channel_id`, `seam`, `request_id`
- Log level from config, not hardcoded
- **Never use `print()` in production code**

```python
import structlog
logger = structlog.get_logger()

logger.info("channel.updated", channel_id=ch_id, value=new_value, status=status)
```

## Configuration

Use `pydantic-settings` with environment variable overrides:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./scada.db"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env")
```

Never hardcode connection strings, ports, or paths.

## Testing

- **Unit tests** — pytest + pytest-asyncio; mock all external I/O
- **Integration tests** — use `httpx.AsyncClient` with `TestClient(app)`
- **Parity tests** — compare Python API output against legacy golden fixtures
- Minimum coverage: all route handlers and all service methods

## Forbidden Patterns

- ❌ No `global` state or module-level mutable singletons
- ❌ No raw `dict` as API return type — always a Pydantic model
- ❌ No `requests` library in async code — use `httpx`
- ❌ No Windows Registry reads — config lives in env vars or `.env` files
- ❌ No COM/ActiveX calls in Python — use abstraction layers
- ❌ No schema migrations during POC — archiver DB is read-only unless seam explicitly needs writes

## Naming Conventions

- Modules: `snake_case`
- Classes: `PascalCase`
- Functions/vars: `snake_case`
- API routes: `kebab-case` (`/api/channel-history`)

## Data Conventions

- Channel ID format: Always `PluginId.ChannelName`
- Channel Status: `Good`, `Bad`, `Unknown` (string enum)
- Timestamps: ISO 8601 UTC (`datetime` with `timezone.utc`)
