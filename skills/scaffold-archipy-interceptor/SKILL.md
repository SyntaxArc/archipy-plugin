---
name: scaffold-archipy-interceptor
description: >-
  Scaffold or wire a helpers/interceptors module for an ArchiPy app. Prefer
  ArchiPy FastAPI/gRPC interceptors before custom ones. Cross-cutting only.
---

# Scaffold ArchiPy Interceptor

## Scope

**Only** `helpers/interceptors/`. Do not create utils or decorators here.

## Before writing files

Ask:

1. Framework: FastAPI, gRPC, or other
2. Sync or async
3. Prefer ArchiPy built-in vs custom
4. Cross-cutting concern (metrics, auth context, logging) — not a use-case

## Prefer ArchiPy

Check `archipy.helpers.interceptors` (FastAPI / gRPC). Prefer AppUtils auto-registration for stock interceptors. Show
registration via DI or framework APIs from docs / `../archipy-docs/reference.md` (Interceptors).

## Custom interceptor

Create under `helpers/interceptors/` — FastAPI middleware sketch:

```python
from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach/propagate an X-Request-ID header — cross-cutting only."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.debug(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
        )
        return response
```

- No domain business writes
- No adapter construction inside the interceptor module
- Wire through `configs/containers.py`, `AppUtils`, or framework middleware registration
- Map errors at the boundary; do not leak raw exceptions

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- Bundled skill reference: `../archipy-docs/reference.md` (Interceptors section)
