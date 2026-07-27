# ArchiPy Consumer Reference

Condensed patterns for **apps that depend on** PyPI `archipy`. Prefer live docs when details differ:

https://syntaxarc.github.io/ArchiPy/

## Install

```bash
# Python 3.14+ and uv
uv add "archipy[redis]"
uv add "archipy[dependency-injection]"
uv add "archipy[postgres-sqlalchemy]"
uv add "archipy[fastapi]"   # HTTP + AppUtils.create_fastapi_app
uv add "archipy[grpc]"      # gRPC + AppUtils create_*_grpc_app
# Combine extras as needed: uv add "archipy[redis,dependency-injection]"
```

Common extras (non-exhaustive): see matrix below. Full list on PyPI / docs.

### Extras matrix

| Extra                       | Use                                                                |
|-----------------------------|--------------------------------------------------------------------|
| `redis`                     | Redis adapter + config                                             |
| `fakeredis`                 | Richer Redis mock for BDD                                          |
| `postgres-sqlalchemy`       | Sync Postgres SQLAlchemy + `@postgres_sqlalchemy_atomic_decorator` |
| `postgres-sqlalchemy-async` | Async Postgres SQLAlchemy + async atomic                           |
| `kafka`                     | Kafka producer/consumer adapters                                   |
| `scylladb`                  | ScyllaDB / Cassandra adapter                                       |
| `minio`                     | MinIO / S3-compatible object storage                               |
| `keycloak`                  | Keycloak auth adapter                                              |
| `fastapi`                   | FastAPI + `AppUtils.create_fastapi_app`                            |
| `grpc`                      | gRPC + `create_grpc_app` / `create_async_grpc_app`                 |
| `dependency-injection`      | `dependency-injector` container helpers                            |
| `behave`                    | Behave BDD helpers for apps                                        |

Plugin scaffolds: `/scaffold-app`, `/scaffold-domain`, `/scaffold-adapter`, `/scaffold-logic`, `/scaffold-service`,
`/scaffold-bdd`, plus helper scaffolds (`utils` / `decorator` / `interceptor`).

See PyPI / docs for the full extras matrix.

## Project layout (apps)

```text
my_app/
├── configs/          # AppConfig(BaseConfig), containers.py
├── models/           # entities, errors, types — data structures only
│   └── dtos/{domain}/
│       ├── domain/v{n}/   # versioned — cross service boundary
│       └── repository/    # internal — never versioned
├── helpers/          # optional app-local; prefer archipy.helpers
│   ├── utils/
│   ├── decorators/
│   └── interceptors/
├── repositories/
│   └── {domain}/
│       ├── adapters/              # domain wrappers (e.g. user_db_adapter.py)
│       └── {domain}_repository.py
├── logics/
│   └── {domain}/         # @atomic unit of work
└── services/
    └── {domain}/v{n}/    # versioned HTTP/gRPC
features/                 # Behave BDD (optional)
```

Import direction: `configs ← models ← helpers ← repositories / logics / services`.

Call flow: `services → logics (@atomic) → repositories → adapters → ArchiPy`.

Live: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/

## DTO naming

| Kind                            | Pattern                                                           | Example                    |
|---------------------------------|-------------------------------------------------------------------|----------------------------|
| Domain input / output           | `{Op}InputDTO` / `{Op}OutputDTO`                                  | `UserRegistrationInputDTO` |
| Repo command / query / response | `{Action}CommandDTO` / `{Action}QueryDTO` / `{Domain}ResponseDTO` | `CreateUserCommandDTO`     |

## BaseConfig

```python
from archipy.configs.base_config import BaseConfig
from archipy.configs.environment_type import EnvironmentType

class AppConfig(BaseConfig):
    def customize(self) -> None:
        super().customize()
        self.FASTAPI.PROJECT_NAME = "my-service"
        self.FASTAPI.RELOAD = self.ENVIRONMENT == EnvironmentType.LOCAL

config = AppConfig()
BaseConfig.set_global(config)
```

- Env vars override defaults (`FASTAPI__SERVE_PORT`, …); document keys in `.env.example`.
- Read with `BaseConfig.global_config()`.

### FastAPIConfig + uvicorn

`config.FASTAPI` drives `AppUtils.create_fastapi_app` **and** uvicorn — never hardcode host/port/reload:

| Area       | Fields                                                  |
|------------|---------------------------------------------------------|
| Serve      | `SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `WORKERS_COUNT`   |
| Proxy      | `PROXY_HEADERS`, `FORWARDED_ALLOW_IPS`                  |
| App / docs | `PROJECT_NAME`, `OPENAPI_URL`, `DOCS_URL`, `RE_DOC_URL` |

```python
config = BaseConfig.global_config()
uvicorn.run(
    "manage:create_app",
    factory=True,
    host=config.FASTAPI.SERVE_HOST,
    port=config.FASTAPI.SERVE_PORT,
    reload=config.FASTAPI.RELOAD,
    proxy_headers=config.FASTAPI.PROXY_HEADERS,
    forwarded_allow_ips=config.FASTAPI.FORWARDED_ALLOW_IPS or "127.0.0.1",
)
```

gRPC bind (parallel): `config.GRPC.SERVE_HOST`, `config.GRPC.SERVE_PORT`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/config_management/

## Adapters (sketch)

```python
from archipy.adapters.redis.adapters import RedisAdapter

redis = RedisAdapter()  # uses global config.REDIS
```

Domain wrappers live under `repositories/{domain}/adapters/` (e.g. `user_db_adapter.py`, `user_cache_adapter.py`).
Prefer thin wrappers around ArchiPy adapters. Map **specific** client errors to domain errors with `raise ... from e`.
Keep sync/async as separate classes. Inject ports into logics/repos.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/

## Logics (unit of work)

- Domain DTO in → domain DTO out; no FastAPI/gRPC imports.
- Public methods: `@postgres_sqlalchemy_atomic_decorator` (or async twin) when using Postgres SQLAlchemy.
- May call other domain logics; **never** another domain’s repository.

## AppUtils (FastAPI + gRPC)

```python
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

app = AppUtils.create_fastapi_app()              # reads FASTAPI config
server = AppUtils.create_grpc_app(BaseConfig.global_config())       # sync
# server = AppUtils.create_async_grpc_app(config)                   # async
```

Do not hand-roll bare `FastAPI()` / `grpc.server()` when extras are installed. Prefer config flags for stock
middleware/interceptors (`FASTAPI.GZIP_MIDDLEWARE_IS_ENABLED`, `GRPC_RATE_LIMIT.IS_ENABLED`).

## Health checks (liveness/readiness/startup)

ArchiPy apps should expose app-level health so infrastructure can route traffic correctly — FastAPI HTTP routes and/or
the standard gRPC Health Checking Protocol. Scaffold with `/scaffold-health-checks`.

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

Combine readiness with shutdown signals:

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
- Not testing probe behavior under failure

## Utils

Prefer ArchiPy utils under `archipy.helpers.utils`:

| Util             | Typical use                  |
|------------------|------------------------------|
| `TracingUtils`   | tracing helpers              |
| `RateLimitUtils` | rate limiting                |
| `DatetimeUtils`  | datetime helpers             |
| `StringUtils`    | string helpers               |
| `JwtUtils`       | JWT encode/decode            |
| `PasswordUtils`  | password hashing             |
| `FileUtils`      | file helpers                 |
| `ErrorUtils`     | error helpers                |
| `AppUtils`       | FastAPI / gRPC app factories |

Custom utils: pure only — no DB/network/adapter construction.

## Decorators

Prefer ArchiPy under `archipy.helpers.decorators`:

| Decorator area               | Examples                                                                             |
|------------------------------|--------------------------------------------------------------------------------------|
| Cache                        | `ttl_cache`                                                                          |
| Transactions (on **logics**) | `postgres_sqlalchemy_atomic_decorator`, `async_postgres_sqlalchemy_atomic_decorator` |
| Observability                | tracing, timing                                                                      |
| Resilience                   | retry, timeout                                                                       |
| Other                        | singleton, rate-limit                                                                |

No concrete adapter imports at module level in custom decorators.

## Interceptors

Prefer ArchiPy under `archipy.helpers.interceptors` (FastAPI / gRPC). Cross-cutting only. Prefer AppUtils
auto-registration for stock hooks; wire custom via DI / `customized_interceptors=` — not business logic.

Live helpers overview: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/

## Dependency injection

```bash
uv add "archipy[dependency-injection]"
```

Wire **ports → adapters → repositories → logics → services** in `configs/containers.py`. Override providers in tests.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/

## Errors

- Subclass ArchiPy domain/system/resource errors from `archipy.models.errors`.
- Raise with context: `raise NotFoundError(...) from e`.
- Do not leak raw driver exceptions into services.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/

## BDD testing

```text
features/
├── *.feature, steps/
├── scenario_context.py
├── scenario_context_pool_manager.py
├── test_helpers.py
├── environment.py
└── test_containers.py   # infra / @needs-* only
```

- Behave (not pytest); `uv add "archipy[behave]"`; infra also `archipy[testcontainers]`.
- Isolate with `ScenarioContext` + pool; hooks in `environment.py` (see `/scaffold-bdd`).
- Tag infra `@needs-*`; skip with `behave --tags=~@needs-redis`.
- Do not copy ArchiPy-core gRPC/Temporal environment blocks unless the app needs them.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

## Quickstart path

1. `uv init` + `uv add "archipy[redis,fastapi]"`
2. `AppConfig` + `set_global` (customize `FASTAPI`)
3. `AppUtils.create_fastapi_app` + domain adapters under `repositories/`
4. Add logics (`@atomic`) / services / optional `features/`

Live: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

## API reference

https://syntaxarc.github.io/ArchiPy/api_reference/
