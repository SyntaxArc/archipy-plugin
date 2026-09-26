# ArchiPy Consumer Reference

Condensed patterns for **apps that depend on** PyPI `archipy`. Prefer live docs when details differ:

https://syntaxarc.github.io/ArchiPy/

Verified against `archipy` 5.4.x. Import symbols from their **full submodule paths** — `archipy.helpers.utils`
and `archipy.configs` package `__init__` files do not re-export symbols.

> **ArchiPy 5.x:** OpenTelemetry replaces the removed Sentry, Elastic APM, and Prometheus integrations. Use
> `BaseConfig.OTEL`, `OtelUtils`, `trace_root` / `trace_span`, and the `otel*` extras described below.

## Topic files

Load only the topic you need:

| Topic | File |
|---|---|
| Configuration and dependency injection | `reference/config.md` |
| Adapters, entities, and unit of work | `reference/adapters.md` |
| Services and AppUtils bootstrap | `reference/services.md` |
| Health checks | `reference/health-checks.md` |
| Helpers: utils, decorators, interceptors | `reference/helpers.md` |
| Observability (OpenTelemetry) | `reference/observability.md` |
| Errors | `reference/errors.md` |
| BDD testing | `reference/testing.md` |

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

> ArchiPy 5.4 SQLAlchemy adapters import `sqlalchemy.ext.asyncio` even on the sync path, and SQLAlchemy 2.1 no longer
> installs `greenlet` by default. With `archipy[postgres,sqlalchemy]`, also add `greenlet` (or use
> `sqlalchemy-async`), or imports fail with "The SQLAlchemy asyncio module requires … 'greenlet'".

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
| `fastapi`                           | FastAPI + `AppUtils.create_fastapi_app`                                         |
| `grpc`                              | gRPC + `create_grpc_app` / `create_async_grpc_app` (+ `grpcio-health-checking`) |
| `dependency-injection`              | `dependency-injector` container helpers                                         |
| `behave`                            | Behave BDD helpers for apps                                                     |
| `testcontainers`                    | Testcontainers for `@needs-*` infra BDD                                         |
| `temporalio`                        | Temporal adapter, worker, runtime                                               |
| `otel`                              | OpenTelemetry SDK + OTLP traces, metrics, and logs                              |
| `otel-fastapi`                      | FastAPI OpenTelemetry instrumentation                                            |
| `otel-grpc`                         | gRPC OpenTelemetry instrumentation                                               |
| `otel-sqlalchemy`                   | SQLAlchemy OpenTelemetry instrumentation                                         |
| `otel-redis`                        | Redis OpenTelemetry instrumentation                                              |
| `otel-elasticsearch`                | Elasticsearch OpenTelemetry instrumentation                                      |
| `otel-kafka`                        | Kafka OpenTelemetry instrumentation                                              |
| `otel-scylladb`                     | ScyllaDB OpenTelemetry instrumentation                                           |
| `otel-minio`                        | MinIO/botocore OpenTelemetry instrumentation                                     |
| `jwt`                               | JWT encode/decode (`JWTUtils`)                                                  |
| `cache`                             | Cache helpers                                                                   |
| `scheduler`                         | Scheduler helpers                                                               |
| `parsian-ipg` / `parsian-ipg-async` | Parsian payment gateway                                                         |
| `saman-ipg`                         | Saman payment gateway                                                           |

Plugin scaffolds: `/scaffold-app`, `/scaffold-domain`, `/scaffold-models`, `/scaffold-adapter`, `/scaffold-logic`,
`/scaffold-service`, `/scaffold-bdd`, `/scaffold-health-checks`, `/redis-search`, plus helper scaffolds (`utils` /
`decorator` / `interceptor`).

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

## Quickstart path

1. `uv init` + `uv add "archipy[redis,fastapi,postgres,sqlalchemy]"` (pick extras you need)
2. `AppConfig` + `set_global` (customize `FASTAPI`)
3. `AppUtils.create_fastapi_app` + domain adapters under `repositories/`
4. Add logics (`*_sqlalchemy_atomic_decorator`) / services / optional `features/`

Live: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

## API reference

https://syntaxarc.github.io/ArchiPy/api_reference/
