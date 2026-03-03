# Python Platform Wrapper Generation Rules

Apply these rules when generating platform abstraction wrappers for Python backends.

## Target Architecture

- **Backend language**: Python 3.12+
- **Backend framework**: FastAPI (async)
- **DI pattern**: FastAPI `Depends()`
- **Logging**: `structlog` with JSON output
- **Testing**: `pytest` + `pytest-asyncio`

---

## Dependency Detection Table

Map legacy platform dependencies to Python wrapper types:

| Legacy Pattern | Source Tech | Wrapper Type | Python Package (real impl) | Notes |
|----------------|-------------|--------------|---------------------------|-------|
| COM/ActiveX/OLE | .NET `Marshal.*`, `[ComImport]`, VB6 `CreateObject` | `ComWrapper` | `pywin32` (`win32com`) | Windows-only runtime |
| Device I/O (Serial) | .NET `SerialPort`, VB6 `MSComm` | `SerialPortWrapper` | `pyserial-asyncio` | Cross-platform |
| Printing | .NET `PrintDocument`, VB6 `Printer` object | `PrintServiceWrapper` | `pywin32` (`win32print`) | Platform-specific |
| Windows Registry | .NET `Microsoft.Win32.Registry`, VB6 registry APIs | **No wrapper** | Move to env vars | Config pattern, not wrapper |
| Named Pipes (IPC) | .NET `System.IO.Pipes.NamedPipe*` | **No wrapper** | Replace with REST/WebSocket | Architecture change |
| WCF Services | .NET `System.ServiceModel.*` | **No wrapper** | Replace with REST/WebSocket | Architecture change |
| Device drivers (custom DLL) | P/Invoke, `DllImport` | `DeviceDriverWrapper` | `ctypes` or vendor SDK | Case-by-case |
| MSMQ | .NET `System.Messaging` | **No wrapper** | Replace with modern queue (Kafka/RabbitMQ) | Architecture change |

**Detection heuristics:**
- If discovery.md mentions "COM", "ActiveX", "OLE", "OPC", "Marshal.*" → `ComWrapper`
- If discovery.md mentions "SerialPort", "COM1", "COM2", "RS-232" → `SerialPortWrapper`
- If discovery.md mentions "PrintDocument", "PrintDialog", "win32print" → `PrintServiceWrapper`
- If discovery.md mentions "Registry", "HKEY_" → Document as config pattern (no wrapper)
- If discovery.md mentions "NamedPipe", "WCF", "ServiceModel" → Document as architecture change (no wrapper)

---

## 3-Tier Wrapper Pattern

### Tier 1: Abstract Base (Interface)

**File**: `backend/app/adapters/{type}_wrapper.py`

**Template**:
```python
"""Abstract interface for {Type} platform dependency."""

from abc import ABC, abstractmethod
from typing import Any


class {Type}Wrapper(ABC):
    """
    Platform abstraction for {description}.

    Implementations:
    - Mock{Type}: Test implementation (no platform dependency)
    - Windows{Type}: Real Windows implementation (pywin32)
    """

    @abstractmethod
    async def operation_name(self, param: str) -> Any:
        """
        [Operation description]

        Args:
            param: [parameter description]

        Returns:
            [return value description]

        Raises:
            [exceptions]
        """
        ...
```

**Rules**:
- All methods must be `async def` (FastAPI convention)
- Use `@abstractmethod` decorator
- Comprehensive docstrings with Args/Returns/Raises
- Type hints for all parameters and returns
- No implementation — only interface definition

---

### Tier 2: Mock Implementation

**File**: `backend/app/adapters/mock_{type}.py`

**Template**:
```python
"""Mock implementation of {Type}Wrapper for testing."""

import structlog
from app.adapters.{type}_wrapper import {Type}Wrapper

logger = structlog.get_logger()


class Mock{Type}({Type}Wrapper):
    """
    Test implementation of {Type}Wrapper.

    Returns realistic test data without requiring actual platform dependency.
    All operations are logged for test verification.
    """

    async def operation_name(self, param: str) -> Any:
        """Mock implementation of operation_name."""
        logger.info(
            "{type}.operation_name.called",
            param=param,
            mock=True,
        )

        # Return realistic test data
        return {"status": "success", "data": "mock_value"}
```

**Rules**:
- Inherit from abstract base
- Log every operation with `structlog`
- Include `mock=True` in log entries
- Return realistic data structures (not just `None` or `"mock"`)
- Must pass unit tests without any platform dependency installed
- Simulate realistic timing (use `await asyncio.sleep(0.01)` for I/O operations)

---

### Tier 3: DI Factory

**File**: `backend/app/dependencies.py` (append to existing file)

**Template**:
```python
from functools import lru_cache
from app.adapters.{type}_wrapper import {Type}Wrapper
from app.config import get_settings


@lru_cache
def get_{type}() -> {Type}Wrapper:
    """
    Dependency injection factory for {Type}Wrapper.

    Returns mock implementation if use_mock_adapters=True in config,
    otherwise returns real Windows implementation.
    """
    if get_settings().use_mock_adapters:
        from app.adapters.mock_{type} import Mock{Type}
        return Mock{Type}()

    # Real implementation (Windows-only, requires pywin32)
    from app.adapters.win_{type} import Windows{Type}
    return Windows{Type}()
```

**Configuration** (add to `backend/app/config.py` if missing):
```python
class Settings(BaseSettings):
    # ... existing settings ...

    use_mock_adapters: bool = True  # Default to mock for development

    model_config = SettingsConfigDict(env_file=".env")
```

**Usage in routes**:
```python
from fastapi import APIRouter, Depends
from app.adapters.{type}_wrapper import {Type}Wrapper
from app.dependencies import get_{type}

router = APIRouter()

@router.post("/endpoint")
async def endpoint(
    {type}: {Type}Wrapper = Depends(get_{type}),
):
    result = await {type}.operation_name("param")
    return result
```

**Rules**:
- Use `@lru_cache` to ensure singleton behavior
- Check `use_mock_adapters` setting
- Import real implementation only inside conditional (fails gracefully if not installed)
- Return type annotation matches abstract base
- Inject via `Depends()` in route handlers
- Never import platform-specific implementations directly in business logic

---

## File Structure

```
backend/
├── app/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── com_wrapper.py          # Abstract base
│   │   ├── mock_com.py             # Mock implementation
│   │   ├── win_com.py              # Real Windows impl (created later)
│   │   ├── serial_port_wrapper.py  # Abstract base
│   │   ├── mock_serial_port.py     # Mock implementation
│   │   └── ...
│   ├── dependencies.py             # DI factories
│   └── config.py                   # Settings with use_mock_adapters
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Abstract base class | `{Type}Wrapper` | `ComWrapper`, `SerialPortWrapper` |
| Mock class | `Mock{Type}` | `MockCom`, `MockSerialPort` |
| Real implementation | `Windows{Type}` or `Native{Type}` | `WindowsCom`, `NativeSerialPort` |
| DI factory function | `get_{type}` | `get_com`, `get_serial_port` |
| File names | `snake_case` | `com_wrapper.py`, `mock_com.py` |

---

## Configuration vs. Wrapper Decision Tree

**Generate wrapper IF:**
- Requires runtime library/DLL/native code
- Has operations that need mocking for tests
- Involves I/O or external process communication

**Document as config pattern (no wrapper) IF:**
- Pure configuration data (registry keys, config files)
- Can be replaced with environment variables
- No runtime operations

**Document as architecture change (no wrapper) IF:**
- IPC mechanism replaced by REST/WebSocket
- Legacy communication pattern not applicable to web architecture
- Requires fundamental architecture rethink

---

## Error Handling

All wrapper methods should raise clear exceptions:

```python
class WrapperException(Exception):
    """Base exception for wrapper errors."""
    pass

class WrapperConnectionError(WrapperException):
    """Device/service connection failed."""
    pass

class WrapperOperationError(WrapperException):
    """Operation failed."""
    pass
```

Mock implementations should simulate errors when appropriate:
```python
async def risky_operation(self, param: str) -> Any:
    if param == "invalid":
        raise WrapperOperationError("Simulated error for testing")
    return {"status": "success"}
```

---

## Testing Pattern

**Unit test template** (`backend/tests/unit/test_mock_{type}.py`):
```python
import pytest
from app.adapters.mock_{type} import Mock{Type}


@pytest.mark.asyncio
async def test_{type}_operation():
    """Test mock {type} operation."""
    wrapper = Mock{Type}()
    result = await wrapper.operation_name("test_param")

    assert result["status"] == "success"
    assert "data" in result


@pytest.mark.asyncio
async def test_{type}_error_handling():
    """Test mock {type} error handling."""
    wrapper = Mock{Type}()

    with pytest.raises(WrapperOperationError):
        await wrapper.operation_name("invalid")
```

---

## What NOT to Do

❌ Do NOT implement business logic in wrappers — only platform abstraction
❌ Do NOT create wrappers for every external library — only platform-specific dependencies
❌ Do NOT use synchronous code — all methods must be `async def`
❌ Do NOT bypass DI — never instantiate wrappers directly in business logic
❌ Do NOT hardcode platform assumptions — use configuration flags
❌ Do NOT implement real platform code (`win_{type}.py`) during initial migration — mock is sufficient for POC
