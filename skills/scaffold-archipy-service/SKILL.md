---
name: scaffold-archipy-service
description: >-
  Scaffold a thin ArchiPy service (FastAPI router or gRPC servicer) and note
  AppUtils / FastAPIConfig bootstrap. Use when adding HTTP/gRPC transport under
  services/{domain}/v{n}/.
---

# Scaffold ArchiPy Service

## Before writing files

Ask the user for:

1. Domain name (e.g. `user`)
2. API version (default `v1`)
3. Transport: FastAPI (default) or gRPC (sync vs async)

## Prefer ArchiPy

```bash
uv add "archipy[fastapi]"   # HTTP
uv add "archipy[grpc]"      # gRPC
```

## Generate

```text
services/<domain>/v{n}/
└── <domain>_service.py
```

### FastAPI

- Thin router: request → domain `*InputDTO` → logic → `*OutputDTO`.
- Export `create_router(container)` (or equivalent) for `manage.py` / app factory.
- Map domain errors to HTTP status; no business rules / `@atomic` here.

### gRPC

- Thin servicer calling logic; sync servicers with `AppUtils.create_grpc_app`, async with `create_async_grpc_app`.
- Do not mix sync/async servicer styles on one server.

## Bootstrap (entrypoint)

Prefer AppUtils — do not hand-roll bare `FastAPI()` / `grpc.server()`:

```python
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

app = AppUtils.create_fastapi_app()
app.include_router(create_user_v1_router(container))
```

uvicorn in `manage.py` from `config.FASTAPI` (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`,
`FORWARDED_ALLOW_IPS`).

## Constraints

- Version in path (`v1`, `v2`), not in business logic.
- Do not re-implement CORS/exception handlers/stock gRPC interceptors AppUtils already wires.
- Wire logic via DI container.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/interceptors/
