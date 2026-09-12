---
name: scaffold-archipy-decorator
description: >-
  Scaffold or wire a helpers/decorators module for an ArchiPy app. Prefer ArchiPy
  decorators (ttl_cache_decorator, postgres_sqlalchemy_atomic_decorator,
  trace_span / trace_root, measure_duration / count_calls, …) before custom ones.
---

# Scaffold ArchiPy Decorator

## Scope

**Only** `helpers/decorators/`. Do not create utils or interceptors here.

## Before writing files

1. Inspect existing decorators, call sites, and the installed ArchiPy version for a matching decorator.
2. Infer sync/async style and project naming from the target call site.
3. Ask only for unresolved behavior. Prefer an ArchiPy decorator whenever it fits.
4. Preserve existing decorator modules; do not overwrite.

## Prefer ArchiPy

Examples:

- `from archipy.helpers.decorators.cache import ttl_cache_decorator`
- `from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator`
- `from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator`
- `trace_span` / `trace_root` (+ async twins) from `archipy.helpers.decorators.tracing`
- `measure_duration` / `count_calls` (+ async twins) from `archipy.helpers.decorators.metrics`
- `timeout_decorator`, `retry_decorator`, `singleton_decorator`, `timing_decorator`, and
  `grpc_rate_limit_decorator` under `archipy.helpers.decorators`

Show correct usage on a sample function; do not reimplement. UoW decorators belong on **logics**, not
services/repositories.

## Custom decorator

Create `helpers/decorators/<name>.py`:

```python
from __future__ import annotations

import functools
import inspect
import logging
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def timed(func: Callable[P, R]) -> Callable[P, R]:
    """Log wall-clock duration of a sync call.

    Args:
        func: Callable to wrap.

    Returns:
        Wrapped callable that logs elapsed milliseconds.

    Raises:
        TypeError: If `func` is a coroutine function — use an async twin instead.

    Example:
        @timed
        def build_report(order_id: str) -> str:
            ...
    """
    if inspect.iscoroutinefunction(func):
        raise TypeError(f"{func.__qualname__} is async; use an async twin instead of timed()")

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.debug("%s took %.2f ms", func.__qualname__, elapsed_ms)

    return wrapper
```

- Use `functools.wraps`
- Preserve types where practical (`ParamSpec` / `TypeVar`)
- Google-style docstring with Args/Returns and a usage example
- **No** concrete adapter imports at module level
- Separate sync/async wrappers if both needed
- Sync wrappers must reject coroutine functions (`inspect.iscoroutinefunction`) — use async twins instead

## Verify

Run formatter/linter and focused tests for return values, exceptions, and metadata/signature preservation. Report the
reused ArchiPy API or files created, plus commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- Bundled skill reference: `../archipy-docs/reference.md` (Decorators section), resolved relative to this `SKILL.md`'s
  directory in the plugin installation — not the app workspace.
