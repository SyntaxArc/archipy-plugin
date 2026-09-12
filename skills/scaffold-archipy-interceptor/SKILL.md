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

1. Inspect app bootstrap, existing interceptors/middleware, DI wiring, and the installed ArchiPy version.
2. Infer framework and sync/async style from the repository.
3. Ask only for an unresolved cross-cutting concern or framework choice. Prefer an ArchiPy interceptor whenever it
   fits.
4. Preserve existing registration order and modules; do not overwrite.

## Prefer ArchiPy

Check `archipy.helpers.interceptors` (FastAPI / gRPC). Prefer AppUtils auto-registration for stock interceptors. Show
registration via DI or framework APIs from docs / `../archipy-docs/reference.md` (Interceptors), resolved relative to
this `SKILL.md`'s directory in the plugin installation — not the app workspace.

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

## Verify

Run formatter/linter and focused transport tests for ordering, success, and mapped failure behavior. Confirm registration
occurs once. Report the reused ArchiPy API or files created, plus commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- Bundled skill reference: `../archipy-docs/reference.md` (Interceptors section)
