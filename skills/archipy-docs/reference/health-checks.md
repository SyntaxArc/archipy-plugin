# ArchiPy Reference: Health checks

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## Health checks (plugin convention)

> **Not a library API.** ArchiPy does not ship HTTP `/health/*` routes or a stock gRPC Health servicer.
> These are **plugin/app conventions** for consumer apps. Scaffold with `/scaffold-health-checks`.
> The `grpc` extra does include `grpcio-health-checking` so apps can register `grpc.health.v1.Health`.

### Probe types

- Liveness: "is the process alive or stuck". Failed liveness triggers a restart. Keep it simple and fast.
- Readiness: "can this instance serve traffic right now". Failed readiness removes the instance from endpoints; it does
  not restart. Put dependency checks here (database, cache, downstream HTTP/gRPC).
- Startup: "has initialization finished". Prevents premature liveness/readiness failures during slow startup.

### FastAPI endpoints

Convention (recommended):

- `GET /health/live` for liveness
- `GET /health/ready` for readiness

Liveness must not call external dependencies.

Safe liveness sketch:

```python
@router.get("/health/live")
async def liveness() -> dict[str, str | float]:
    return {
        "status": "ok",
        "uptime_seconds": time.monotonic() - start_time,
    }
```

Readiness should run dependency checks with timeouts and return:

- `200` when all checks are healthy
- `503` when any check fails
- a per-check payload so you can see exactly what broke

Example readiness payload shape:

```json
{
  "status": "not_ready",
  "checks": {
    "database": { "healthy": false, "error": "..." },
    "cache": { "healthy": true }
  }
}
```

### gRPC Health protocol

Prefer `grpcio-health-checking` (`grpc.health.v1.Health`) — do not invent a custom health RPC.

Register service names:

| Service       | Meaning                                        |
|---------------|------------------------------------------------|
| `""` (empty)  | Overall readiness (default Check target)       |
| `"readiness"` | Explicit readiness (deps + warm-up + shutdown) |
| `"liveness"`  | Process-only liveness (no dependency checks)   |

Initial status at register time — **`""` and `"readiness"` start `NOT_SERVING`** until warm-up + deps are healthy:

```python
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

health_servicer = health.HealthServicer()
health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
health_servicer.set("liveness", health_pb2.HealthCheckResponse.SERVING)
health_servicer.set("readiness", health_pb2.HealthCheckResponse.NOT_SERVING)
health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
```

Wire onto `AppUtils.create_grpc_app` / `create_async_grpc_app`. Update `""` / `"readiness"` from shared check helpers;
never flip `"liveness"` for dependency failures. On shutdown: set readiness/`""` to
`NOT_SERVING`, then `health_servicer.enter_graceful_shutdown()`.

### Kubernetes configuration notes

HTTP:

- Startup / liveness → `/health/live`
- Readiness → `/health/ready` with `successThreshold: 2`

gRPC:

```yaml
livenessProbe:
  grpc:
    port: 50051
    service: liveness
readinessProbe:
  grpc:
    port: 50051
    service: readiness
  successThreshold: 2
```

- Set `timeoutSeconds` high enough for the slowest readiness dependency check.
- Ports should match `config.FASTAPI.SERVE_PORT` / `config.GRPC.SERVE_PORT`.

### Graceful shutdown

1. Receive `SIGTERM`
2. Make readiness fail immediately (HTTP `503` / gRPC `NOT_SERVING`)
3. Wait briefly so in-flight requests drain

Optionally add Kubernetes `preStop` sleep for extra safety.

### Common mistakes

- Putting dependency checks in liveness (HTTP path or gRPC `"liveness"` service)
- No timeout on dependency checks (probes hang until infra times out)
- Returning healthy while dependencies are down (HTTP `200` or gRPC `SERVING`)
- Hand-rolling a custom gRPC health RPC instead of `grpc.health.v1.Health`
- Mixing sync and async gRPC servicers on one server
- Starting `""` as `SERVING` before warm-up completes
- Not testing probe behavior under failure
