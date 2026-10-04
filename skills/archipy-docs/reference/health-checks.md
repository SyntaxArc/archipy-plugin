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

Health responses must not describe the service: no dependency names, versions, hostnames, error text, or uptime. Probes
only need the status code, so a public or cluster-visible endpoint must not reveal what the service is built on.

Safe liveness sketch:

```python
@router.get("/health/live")
async def liveness() -> Response:
    return Response(status_code=status.HTTP_200_OK)
```

Readiness should run dependency checks with timeouts and return:

- `200` with an empty body when all required checks are healthy
- `503` with an empty body (or the generic `UnavailableError` body) when a required check fails
- per-check detail **in server logs only** (`logger.warning(..., exc_info=True)`), never in the response

Layering for the checks: the readiness logic calls a `HealthCheckRepository`; the repository calls one adapter per
dependency under `repositories/health_check/adapters/` (one file each, e.g. `health_check_postgres_adapter.py`,
`health_check_minio_adapter.py`). Each adapter catches its client's specific errors and raises `UnavailableError` with
`raise ... from e`. The logic catches only `UnavailableError` / `TimeoutError` for soft dependencies. Logics never
import or call ArchiPy adapters, run raw SQL, or return `"ok"` without actually probing.

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
- Returning dependency names, versions, hostnames, or error messages in a health response
- A probe that reports `ok` without calling the dependency (for example a hardcoded Temporal `"ok"`)
- Driving adapters or raw SQL from the readiness logic instead of going through a repository
- Hand-rolling a custom gRPC health RPC instead of `grpc.health.v1.Health`
- Mixing sync and async gRPC servicers on one server
- Starting `""` as `SERVING` before warm-up completes
- Not testing probe behavior under failure
