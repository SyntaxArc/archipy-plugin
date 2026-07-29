# ArchiPy Consumer Reference

Condensed patterns for **apps that depend on** PyPI `archipy`. Prefer live docs when details differ:

https://syntaxarc.github.io/ArchiPy/

Verified against `archipy` 4.17.x. Import symbols from their **full submodule paths** — `archipy.helpers.utils`
and `archipy.configs` package `__init__` files do not re-export symbols.

## Install

```bash
# Python 3.14+ and uv
uv add "archipy[redis]"
uv add "archipy[dependency-injection]"
uv add "archipy[postgres,sqlalchemy]"          # sync Postgres + SQLAlchemy
uv add "archipy[postgres,sqlalchemy-async]"    # async Postgres + SQLAlchemy
uv add "archipy[fastapi]"   # HTTP + AppUtils.create_fastapi_app
uv add "archipy[grpc]"      # gRPC + AppUtils create_*_grpc_app
# Combine extras: uv add "archipy[redis,dependency-injection,fastapi]"
```

### Extras matrix (published)

| Extra                               | Use                                                                             |
|-------------------------------------|---------------------------------------------------------------------------------|
| `redis`                             | Redis adapter + RediSearch (`search_index`) + config                            |
| `fakeredis`                         | Richer Redis mock for BDD                                                       |
| `postgres`                          | `psycopg` driver / pool                                                         |
| `sqlalchemy`                        | Sync SQLAlchemy + atomic decorators                                             |
| `sqlalchemy-async`                  | Async SQLAlchemy + async atomic                                                 |
| `aiosqlite`                         | SQLite async driver                                                             |
| `starrocks`                         | StarRocks sync SQLAlchemy                                                       |
| `starrocks-async`                   | StarRocks async SQLAlchemy                                                      |
| `kafka`                             | Kafka producer/consumer adapters                                                |
| `scylladb`                          | ScyllaDB / Cassandra adapter                                                    |
| `minio`                             | MinIO / S3-compatible object storage                                            |
| `keycloak`                          | Keycloak auth adapter + `KeycloakUtils`                                         |
| `elasticsearch`                     | Elasticsearch adapter                                                           |
| `elasticsearch-async`               | Async Elasticsearch adapter                                                     |
| `elastic-apm`                       | Elastic APM integration                                                         |
| `fastapi`                           | FastAPI + `AppUtils.create_fastapi_app`                                         |
| `grpc`                              | gRPC + `create_grpc_app` / `create_async_grpc_app` (+ `grpcio-health-checking`) |
| `dependency-injection`              | `dependency-injector` container helpers                                         |
| `behave`                            | Behave BDD helpers for apps                                                     |
| `testcontainers`                    | Testcontainers for `@needs-*` infra BDD                                         |
| `temporalio`                        | Temporal adapter, worker, runtime                                               |
| `prometheus`                        | Prometheus metrics (+ metric interceptors)                                      |
| `sentry`                            | Sentry integration                                                              |
| `jwt`                               | JWT encode/decode (`JWTUtils`)                                                  |
| `cache`                             | Cache helpers                                                                   |
| `scheduler`                         | Scheduler helpers                                                               |
| `parsian-ipg` / `parsian-ipg-async` | Parsian payment gateway                                                         |
| `saman-ipg`                         | Saman payment gateway                                                           |

Plugin scaffolds: `/scaffold-app`, `/scaffold-domain`, `/scaffold-adapter`, `/scaffold-logic`, `/scaffold-service`,
`/scaffold-bdd`, `/scaffold-health-checks`, `/redis-search`, plus helper scaffolds (`utils` / `decorator` /
`interceptor`).

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
│   └── {domain}/         # unit of work (atomic decorators)
└── services/
    └── {domain}/v{n}/    # versioned HTTP/gRPC
features/                 # Behave BDD (optional)
```

Import direction: `configs ← models ← helpers ← repositories / logics / services`.

Call flow: `services → logics (atomic UoW) → repositories → adapters → ArchiPy`.

> **Plugin shorthand:** docs sometimes write `@atomic` to mean
> `postgres_sqlalchemy_atomic_decorator` / `async_postgres_sqlalchemy_atomic_decorator`
> (or the sqlite/starrocks/generic twins). There is **no** decorator named `atomic`.

Live: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/

## DTO naming

| Kind                            | Pattern                                                           | Example                    |
|---------------------------------|-------------------------------------------------------------------|----------------------------|
| Domain input / output           | `{Op}InputDTO` / `{Op}OutputDTO`                                  | `UserRegistrationInputDTO` |
| Repo command / query / response | `{Action}CommandDTO` / `{Action}QueryDTO` / `{Domain}ResponseDTO` | `CreateUserCommandDTO`     |

Also available under `archipy.models.dtos`: pagination / sort / search-input DTOs (`range_dtos` and related), and a
protobuf DTO base for gRPC payloads. Prefer those before inventing page/cursor shapes.

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
BaseConfig.set_global(config)  # auto-invokes customize()
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

Also: `FastAPIRateLimitConfig` for FastAPI rate-limit settings; enable gRPC rate-limit via
`GRPC_RATE_LIMIT.IS_ENABLED`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/config_management/

## Adapters (sketch)

```python
from archipy.adapters.redis.adapters import RedisAdapter

redis = RedisAdapter()  # uses global config.REDIS
```

Domain wrappers live under `repositories/{domain}/adapters/` (e.g. `user_db_adapter.py`, `user_cache_adapter.py`).
Prefer thin wrappers around ArchiPy adapters. Map **specific** client errors to domain errors with `raise ... from e`.
Keep sync/async as separate classes. Inject ports into logics/repos.

### Adapter families (library)

Use ArchiPy before inventing clients — extras as above:

| Family                                   | Notes                                                           |
|------------------------------------------|-----------------------------------------------------------------|
| Redis (+ RediSearch)                     | `RedisAdapter.search_index(name)` → handle; see `/redis-search` |
| Postgres / SQLite / StarRocks SQLAlchemy | sync + async adapters; pair with atomic decorators              |
| Kafka, ScyllaDB, MinIO, Keycloak         | dedicated adapters                                              |
| Elasticsearch (+ async)                  | search / document APIs                                          |
| Email                                    | email adapter                                                   |
| Temporal                                 | adapter + `worker.py` / `runtime.py`                            |
| Parsian / Saman IPG                      | Iranian payment gateways                                        |

### Redis Search (library API)

```python
from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.dtos.redis.search.index_schema_dto import (
    IndexSchemaDTO,
    TagFieldConfig,
    TextFieldConfig,
)
from archipy.models.dtos.redis.search.search_query_dto import SearchQueryDTO
from archipy.models.types.redis_search_types import RedisIndexType

redis = RedisAdapter()
handle = redis.search_index("products")
# redis.list_search_indexes()

schema = IndexSchemaDTO(
    fields=[
        TextFieldConfig(name="title"),
        TagFieldConfig(name="category"),
    ],
    index_type=RedisIndexType.HASH,
)
handle.create_index(schema, prefix="product:")
handle.upsert_hash("product:1", {"title": "Redis Guide", "category": "books"})
result = handle.search(SearchQueryDTO(query="@title:Redis", offset=0, limit=20))
```

Do **not** call raw `client.ft()` in app adapters when the handle API covers the case. DTOs live under
`archipy.models.dtos.redis.search.*`; types under `archipy.models.types.redis_search_types`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/

## Entities (SQLAlchemy)

Prefer ArchiPy base entities:

```python
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity
```

App entities subclass library bases (`UpdatableEntity`, `DeletableEntity`, …); keep I/O out of `models/`.

## SessionManagerRegistry + atomic family

Atomic decorators resolve the active SQLAlchemy session through
`archipy.adapters.base.sqlalchemy.session_manager_registry.SessionManagerRegistry`. Register the app's session manager
at bootstrap; BDD hooks call `SessionManagerRegistry.reset()` after each scenario.

| Decorator                                                     | Extra / stack                   |
|---------------------------------------------------------------|---------------------------------|
| `postgres_sqlalchemy_atomic_decorator`                        | `postgres` + `sqlalchemy`       |
| `async_postgres_sqlalchemy_atomic_decorator`                  | `postgres` + `sqlalchemy-async` |
| `sqlite_sqlalchemy_atomic_decorator` / `async_sqlite_…`       | SQLite stacks                   |
| `starrocks_sqlalchemy_atomic_decorator` / `async_starrocks_…` | StarRocks stacks                |
| `sqlalchemy_atomic_decorator`                                 | Generic SQLAlchemy              |

Import from `archipy.helpers.decorators.sqlalchemy_atomic` (lazy-loaded via
`archipy.helpers.decorators` `__getattr__` so SQLAlchemy is not a hard import).

## Logics (unit of work)

- Domain DTO in → domain DTO out; no FastAPI/gRPC imports.
- Public methods: decorate with the matching `*_sqlalchemy_atomic_decorator` when using SQLAlchemy.
- May call other domain logics (nested atomic reuses the open session); **never** another domain's repository.

## AppUtils (FastAPI + gRPC)

```python
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

app = AppUtils.create_fastapi_app()              # config optional; reads global FASTAPI
server = AppUtils.create_grpc_app(BaseConfig.global_config())       # sync — config required
# server = AppUtils.create_async_grpc_app(config)                   # async
```

Do not hand-roll bare `FastAPI()` / `grpc.server()` when extras are installed. Prefer config flags for stock
middleware/interceptors (`FASTAPI.GZIP_MIDDLEWARE_IS_ENABLED`, `GRPC_RATE_LIMIT.IS_ENABLED`). Custom gRPC interceptors:
`customized_interceptors=` on the gRPC factories.

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

## Utils

Prefer ArchiPy utils. Import from the **concrete submodule** (package `__init__` does not re-export):

| Util              | Import path                              | Typical use                     |
|-------------------|------------------------------------------|---------------------------------|
| `AppUtils`        | `archipy.helpers.utils.app_utils`        | FastAPI / gRPC app factories    |
| `BaseUtils`       | `archipy.helpers.utils.base_utils`       | Shared facade helpers           |
| `TracingUtils`    | `archipy.helpers.utils.tracing_utils`    | tracing helpers                 |
| `RateLimitUtils`  | `archipy.helpers.utils.rate_limit_utils` | rate limiting                   |
| `DatetimeUtils`   | `archipy.helpers.utils.datetime_utils`   | datetime helpers                |
| `StringUtils`     | `archipy.helpers.utils.string_utils`     | string helpers                  |
| `JWTUtils`        | `archipy.helpers.utils.jwt_utils`        | JWT encode/decode (`jwt` extra) |
| `PasswordUtils`   | `archipy.helpers.utils.password_utils`   | password hashing                |
| `FileUtils`       | `archipy.helpers.utils.file_utils`       | file helpers                    |
| `ErrorUtils`      | `archipy.helpers.utils.error_utils`      | error helpers                   |
| `TOTPUtils`       | `archipy.helpers.utils.totp_utils`       | TOTP                            |
| `KeycloakUtils`   | `archipy.helpers.utils.keycloak_utils`   | Keycloak helpers                |
| `PrometheusUtils` | `archipy.helpers.utils.prometheus_utils` | Prometheus helpers              |

Custom utils: pure only — no DB/network/adapter construction.

## Decorators

Prefer ArchiPy under `archipy.helpers.decorators`:

| Area                         | Symbols                                                                                                                   |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Cache                        | `ttl_cache_decorator` (`archipy.helpers.decorators.cache`)                                                                |
| Transactions (on **logics**) | `postgres_sqlalchemy_atomic_decorator`, `async_postgres_sqlalchemy_atomic_decorator`, plus sqlite/starrocks/generic twins |
| Observability                | `capture_span`, `capture_transaction` (+ `async_capture_span`, `async_capture_transaction`); `timing_decorator`           |
| Resilience                   | `retry_decorator`, `timeout_decorator`                                                                                    |
| Other                        | `singleton_decorator`, `grpc_rate_limit_decorator` (gRPC only)                                                            |

No concrete adapter imports at module level in custom decorators.

## Interceptors

Prefer ArchiPy under `archipy.helpers.interceptors` (FastAPI / gRPC). Cross-cutting only. Prefer AppUtils
auto-registration for stock hooks; wire custom via DI / `customized_interceptors=` — not business logic.

### Rate-limit and metric interceptors

- FastAPI rate-limit: config via `FastAPIRateLimitConfig`; prefer AppUtils / config flags over manual wiring.
- gRPC rate-limit: `GRPC_RATE_LIMIT.IS_ENABLED` + `grpc_rate_limit_decorator` / stock interceptors.
- **Metric interceptors require `archipy[prometheus]`** — they import `prometheus_client` at module import time. Without
  the extra, importing those modules fails.

Live helpers overview: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/

## Observability

Combine library pieces rather than inventing a parallel stack:

| Concern         | ArchiPy pieces                                                            | Extra         |
|-----------------|---------------------------------------------------------------------------|---------------|
| Tracing / APM   | `TracingUtils`, `capture_span` / `capture_transaction`, Elastic APM hooks | `elastic-apm` |
| Metrics         | `PrometheusUtils`, metric interceptors                                    | `prometheus`  |
| Errors / events | Sentry integration                                                        | `sentry`      |
| Timing          | `timing_decorator`                                                        | —             |

Wire via `AppUtils` + config flags when possible. Health probes (above) are complementary but separate — probes answer
infra routing; observability answers product/ops insight.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/observability/

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
- Reset `SessionManagerRegistry` after scenarios.
- Do not copy ArchiPy-core gRPC/Temporal environment blocks unless the app needs them.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

## Quickstart path

1. `uv init` + `uv add "archipy[redis,fastapi,postgres,sqlalchemy]"` (pick extras you need)
2. `AppConfig` + `set_global` (customize `FASTAPI`)
3. `AppUtils.create_fastapi_app` + domain adapters under `repositories/`
4. Add logics (`*_sqlalchemy_atomic_decorator`) / services / optional `features/`

Live: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

## API reference

https://syntaxarc.github.io/ArchiPy/api_reference/
