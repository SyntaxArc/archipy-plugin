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

- Export a thin router for:
    - `GET /health/live`
    - `GET /health/ready`
- Return `200` healthy, `503` not ready / unhealthy.
- Wire with `include_router` into `manage.py` / app factory.

### Liveness (HTTP)

- Ask: "Is process alive enough to restart if broken?"
- Keep simple and fast. No DB / Redis / downstream checks.
- Safe default:

```python
@router.get("/health/live")
async def liveness() -> dict[str, str | float]:
    return {
        "status": "ok",
        "uptime_seconds": time.monotonic() - start_time,
    }
```

- Optional heartbeat mode for deadlock detection only when user asks.

### Readiness (HTTP)

- Ask: "Can this instance serve traffic right now?"
- Dependency checks here, not in liveness. Include warm-up + shutdown state.
- Per-check detail required:

```python
{
    "status": "not_ready",
    "checks": {
        "database": {"healthy": False, "error": "..."},
        "cache": {"healthy": True},
        "warm_up": {"healthy": True, "detail": "initialization complete"},
    },
}
```

- Each dependency check must use a timeout. Return `503` when any check fails.

## gRPC (`health_grpc_service.py`)

Use the standard gRPC Health Checking Protocol (`grpc.health.v1.Health`) via `grpcio-health-checking`.

### Service names

Register at least:

| Service name  | Role                                            |
|---------------|-------------------------------------------------|
| `""` (empty)  | Overall server readiness (default Check target) |
| `"readiness"` | Explicit readiness (deps + warm-up + shutdown)  |
| `"liveness"`  | Process-only liveness (no dependency checks)    |

Map status:

- Ready / alive → `HealthCheckResponse.SERVING`
- Not ready / shutting down / failed deps → `HealthCheckResponse.NOT_SERVING`

### Wire sketch

```python
from grpc_health.v1 import health, health_pb2, health_pb2_grpc


def register_health_servicer(server, container) -> health.HealthServicer:
    """Attach standard Health servicer; return handle for status updates."""
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("liveness", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("readiness", health_pb2.HealthCheckResponse.NOT_SERVING)
    return health_servicer
```

### Status update rules

- On warm-up complete + deps healthy: set `""` and `"readiness"` to `SERVING`.
- On dep failure: set `""` and `"readiness"` to `NOT_SERVING`. Never flip `"liveness"` for dep failures.
- Keep `"liveness"` at `SERVING` unless the process itself is broken (optional heartbeat).
- Refresh readiness from shared check helpers on a short interval or on notable state changes — do not run slow dep
  checks inside every `Check` if that starves the server; prefer background updater calling `set()`.
- On `SIGTERM`: set readiness/`""` to `NOT_SERVING`, then call `health_servicer.enter_graceful_shutdown()` so future
  `set()` calls are ignored.

### Async gRPC

- Same Health protocol and service-name rules.
- Register on the async server from `AppUtils.create_async_grpc_app`.
- Keep status updates thread-/task-safe; do not block the event loop on dep checks.

## Startup probes

Protect slow-starting services from premature liveness failures.

- HTTP: point startup at `/health/live`.
- gRPC: point startup at service `"liveness"` (or `""` only if overall starts as SERVING early — prefer `"liveness"`).

```yaml
# HTTP
startupProbe:
  httpGet:
    path: /health/live
    port: 8080
  failureThreshold: 20
  periodSeconds: 5
  timeoutSeconds: 3

# gRPC
startupProbe:
  grpc:
    port: 50051
    service: liveness
  failureThreshold: 20
  periodSeconds: 5
  timeoutSeconds: 3
```

## Kubernetes probe YAML

When requested, emit `deploy/k8s-probes.yaml` matching the chosen transport (s).

### HTTP shape

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]

startupProbe:
  httpGet:
    path: /health/live
    port: 8080
  failureThreshold: 20
  periodSeconds: 5
  timeoutSeconds: 3

livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  periodSeconds: 10
  failureThreshold: 3
  timeoutSeconds: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 2
  timeoutSeconds: 3
```

### gRPC shape

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]

startupProbe:
  grpc:
    port: 50051
    service: liveness
  failureThreshold: 20
  periodSeconds: 5
  timeoutSeconds: 3

livenessProbe:
  grpc:
    port: 50051
    service: liveness
  periodSeconds: 10
  failureThreshold: 3
  timeoutSeconds: 3

readinessProbe:
  grpc:
    port: 50051
    service: readiness
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 2
  timeoutSeconds: 3
```

Use `config.GRPC.SERVE_PORT` / `config.FASTAPI.SERVE_PORT` values — never hardcode ports in app code; YAML may show
placeholders matching config.

Rules for both:

- `readinessProbe.successThreshold: 2`
- `failureThreshold: 3` default
- `timeoutSeconds` ≥ slowest readiness check timeout
- `preStop` sleep for short drain window

## Graceful shutdown

- On `SIGTERM`, fail readiness immediately (HTTP `503` / gRPC `NOT_SERVING`).
- Give Kubernetes a short window to stop routing.
- Then exit after in-flight requests finish.

HTTP:

```python
if shutdown_event.is_set():
    return JSONResponse(status_code=503, content={"status": "shutting_down"})
```

gRPC:

```python
health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
health_servicer.set("readiness", health_pb2.HealthCheckResponse.NOT_SERVING)
health_servicer.enter_graceful_shutdown()
```

Use app shutdown delay and/or K8s `preStop` sleep.

## Common mistakes

- Putting dependency checks in liveness (HTTP path or gRPC `"liveness"` service)
- Returning healthy while dependencies are down (HTTP `200` or gRPC `SERVING`)
- No timeout on dependency checks
- No warm-up or shutdown awareness
- Hand-rolling a custom gRPC health RPC instead of `grpc.health.v1.Health`
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
