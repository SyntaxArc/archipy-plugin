---
name: scaffold-archipy-health-checks
description: >-
  Scaffold ArchiPy FastAPI and/or gRPC health checks for liveness, readiness,
  and optional Kubernetes probe YAML. Use when adding app-level health checks,
  startup safety, and graceful shutdown behavior.
---

# Scaffold ArchiPy Health Checks

## Before writing files

Ask the user for:

1. Python package name
2. Transport: FastAPI (HTTP), gRPC (sync or async), or both
3. Dependencies to check in readiness (`postgres`, `redis`, downstream HTTP/gRPC, custom)
4. Optional: heartbeat-based liveness deadlock detection for HTTP (`yes` / `no`)
5. Optional: emit `deploy/k8s-probes.yaml` (`yes` / `no`)

## Prefer ArchiPy

Health checks are app code. ArchiPy does not ship stock HTTP routes or a stock gRPC `Health` servicer.

**Probe semantics** (liveness vs readiness vs startup, K8s notes, common mistakes, FastAPI sketches): keep
`../archipy-docs/reference.md` § Health checks as the source of truth — do not invent alternate probe meanings or
duplicate endpoint sketches here.

```bash
uv add "archipy[fastapi]"   # HTTP probes
uv add "archipy[grpc]"      # gRPC server; also need grpcio-health-checking
```

For gRPC health protocol:

```bash
uv add grpcio-health-checking
```

Prefer existing app bootstrap:

```python
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

# FastAPI
app = AppUtils.create_fastapi_app()
app.include_router(create_health_v1_router(container))

# gRPC (sync)
server = AppUtils.create_grpc_app(BaseConfig.global_config())
# register domain servicers, then health:
register_health_servicer(server, container)

# gRPC (async)
server = AppUtils.create_async_grpc_app(BaseConfig.global_config())
```

Do not hand-roll bare `FastAPI()` / `grpc.server()` when AppUtils is in use. Do not mix sync and async gRPC servicer
styles on one server.

## Generate

```text
<package>/services/health/v1/
├── health_checks.py       # shared readiness helpers (deps, warm-up, shutdown)
├── health_service.py      # FastAPI — when HTTP requested
└── health_grpc_service.py # gRPC HealthServicer wiring — when gRPC requested
deploy/
└── k8s-probes.yaml        # optional (httpGet and/or grpc probes)
```

Share readiness helpers across transports. Keep business rules out of transport files.

## FastAPI (`health_service.py`)

- Export a thin router for `GET /health/live` and `GET /health/ready`.
- Return `200` healthy, `503` not ready / unhealthy.
- Wire with `include_router` into `manage.py` / app factory.
- Liveness: process-only, no deps. Readiness: deps + warm-up + shutdown, timeouts, per-check detail.
- Optional heartbeat mode for deadlock detection only when user asks.
- Code sketches and payload shapes: `../archipy-docs/reference.md` § Health checks → FastAPI endpoints.

## gRPC (`health_grpc_service.py`)

Use the standard gRPC Health Checking Protocol (`grpc.health.v1.Health`) via `grpcio-health-checking`.

Register at least `""` (overall), `"readiness"`, and `"liveness"`. Map ready/alive → `SERVING`, not ready →
`NOT_SERVING`. Full service-name table and update rules: `../archipy-docs/reference.md` § Health checks → gRPC Health
protocol.

### Wire sketch

**`""` and `"readiness"` start `NOT_SERVING`** until warm-up + deps are healthy:

```python
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


def register_health_servicer(server, container) -> health.HealthServicer:
    """Attach standard Health servicer; return handle for status updates."""
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    health_servicer.set("liveness", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("readiness", health_pb2.HealthCheckResponse.NOT_SERVING)
    health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
    return health_servicer
```

### Status update rules (summary)

- Warm-up complete + deps healthy → set `""` and `"readiness"` to `SERVING`.
- Dep failure → `""` / `"readiness"` to `NOT_SERVING`; never flip `"liveness"` for dep failures.
- Prefer background updater calling `set()` over slow checks inside every `Check`.
- On `SIGTERM`: set readiness/`""` to `NOT_SERVING`, then `health_servicer.enter_graceful_shutdown()`.
- Async gRPC: same protocol/names; register on `AppUtils.create_async_grpc_app`; keep updates task-safe.

## Startup probes

- HTTP: point startup at `/health/live`.
- gRPC: point startup at service `"liveness"` (prefer over `""`).

## Kubernetes probe YAML

When requested, emit `deploy/k8s-probes.yaml` matching the chosen transport (s).

**Copy templates from `reference/`, adapt ports to config:**

| Transport | Template                         |
|-----------|----------------------------------|
| HTTP      | `reference/k8s-probes-http.yaml` |
| gRPC      | `reference/k8s-probes-grpc.yaml` |

Use `config.GRPC.SERVE_PORT` / `config.FASTAPI.SERVE_PORT` — never hardcode ports in app code; YAML may show
placeholders matching config.

Rules: `readinessProbe.successThreshold: 2`, `failureThreshold: 3` default, `timeoutSeconds` ≥ slowest readiness check
timeout, `preStop` sleep for short drain window.

## Graceful shutdown

- On `SIGTERM`, fail readiness immediately (HTTP `503` / gRPC `NOT_SERVING`).
- Give Kubernetes a short window to stop routing, then exit after in-flight requests finish.
- Details: `../archipy-docs/reference.md` § Health checks → Graceful shutdown.

## Common mistakes

See `../archipy-docs/reference.md` § Health checks → Common mistakes. Also avoid:

- No warm-up or shutdown awareness in readiness helpers
- Mixing sync and async gRPC health / domain servicers on one server
- Not testing failure behavior by taking down dependencies

## Constraints

- Double quotes, Google-style docstrings, `X | Y` typing
- Keep services thin; no business rules in health transport
- No secrets in code; list env keys separately when needed
- Prefer FastAPI `JSONResponse` for HTTP probes; prefer `grpcio-health-checking` for gRPC
- Suggest `/docs-health-checks` for explanation and `/docs-observability` for metrics / tracing follow-up

## Beyond Kubernetes

Same pattern applies to ALB, Consul, Nginx, or gRPC load balancers: expose health (HTTP and/or `grpc.health.v1`), define
healthy clearly, and let infrastructure stop routing to unhealthy instances.
