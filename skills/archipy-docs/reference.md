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

Common extras (non-exhaustive): `redis`, `postgres-sqlalchemy`, `postgres-sqlalchemy-async`, `kafka`, `scylladb`,
`minio`, `keycloak`, `fastapi`, `grpc`, `dependency-injection`, `behave`.

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

| Kind | Pattern | Example |
|------|---------|---------|
| Domain input / output | `{Op}InputDTO` / `{Op}OutputDTO` | `UserRegistrationInputDTO` |
| Repo command / query / response | `{Action}CommandDTO` / `{Action}QueryDTO` / `{Domain}ResponseDTO` | `CreateUserCommandDTO` |

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

| Area | Fields |
|------|--------|
| Serve | `SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `WORKERS_COUNT` |
| Proxy | `PROXY_HEADERS`, `FORWARDED_ALLOW_IPS` |
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

| Decorator area | Examples |
|----------------|----------|
| Cache | `ttl_cache` |
| Transactions (on **logics**) | `postgres_sqlalchemy_atomic_decorator`, `async_postgres_sqlalchemy_atomic_decorator` |
| Observability | tracing, timing |
| Resilience | retry, timeout |
| Other | singleton, rate-limit |

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
features/*.feature, steps/, scenario_context.py, scenario_context_pool_manager.py, environment.py
```

- Behave (not pytest) as primary style; `uv add "archipy[behave]"` when needed.
- Inject mocks/ports (`RedisMock`); isolate with `ScenarioContext`.
- Tag infra scenarios `@needs-*`; skip with `behave --tags=~@needs-redis`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

## Quickstart path

1. `uv init` + `uv add "archipy[redis,fastapi]"`
2. `AppConfig` + `set_global` (customize `FASTAPI`)
3. `AppUtils.create_fastapi_app` + domain adapters under `repositories/`
4. Add logics (`@atomic`) / services / optional `features/`

Live: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

## API reference

https://syntaxarc.github.io/ArchiPy/api_reference/
