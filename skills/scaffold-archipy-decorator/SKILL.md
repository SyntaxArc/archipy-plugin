---
name: scaffold-archipy-decorator
description: >-
  Scaffold or wire a helpers/decorators module for an ArchiPy app. Prefer ArchiPy
  decorators (ttl_cache, postgres_sqlalchemy_atomic_decorator, tracing, …) before custom ones.
---

# Scaffold ArchiPy Decorator

## Scope

**Only** `helpers/decorators/`. Do not create utils or interceptors here.

## Before writing files

Ask:

1. Decorator purpose (cache, atomic, retry, timing, …)
2. Prefer ArchiPy built-in vs custom
3. Sync, async, or both

## Prefer ArchiPy

Examples:

- `from archipy.helpers.decorators.cache import ttl_cache`
- `from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator`
- `from archipy.helpers.decorators.sqlalchemy_atomic import async_postgres_sqlalchemy_atomic_decorator`
- tracing / timeout / retry / singleton under `archipy.helpers.decorators`

Show correct usage on a sample function; do not reimplement. UoW decorators belong on **logics**, not services/repositories.

## Custom decorator

Create `helpers/decorators/<name>.py`:

```python
from __future__ import annotations

import functools
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

    Example:
        @timed
        def build_report(order_id: str) -> str:
            ...
    """

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

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- Bundled skill reference: `../archipy-docs/reference.md` (Decorators section)
