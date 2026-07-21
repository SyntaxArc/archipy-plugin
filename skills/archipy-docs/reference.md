# ArchiPy Consumer Reference

Condensed patterns for **apps that depend on** PyPI `archipy`. Prefer live docs when details differ:

https://syntaxarc.github.io/ArchiPy/

## Install

```bash
# Python 3.14+ and uv
uv add "archipy[redis]"
uv add "archipy[dependency-injection]"
uv add "archipy[postgres-sqlalchemy]"
# Combine extras as needed: uv add "archipy[redis,dependency-injection]"
```

Common extras (non-exhaustive): `redis`, `postgres-sqlalchemy`, `postgres-sqlalchemy-async`, `kafka`, `scylladb`, `minio`, `keycloak`, `fastapi`, `grpc`, `dependency-injection`, `behave`.

See PyPI / docs for the full extras matrix.

## Project layout (apps)

```text
my_app/
├── configs/          # AppConfig(BaseConfig), containers.py
├── models/           # dtos, entities, errors
├── adapters/         # ports + adapters (+ optional mocks)
├── helpers/
│   ├── utils/
│   ├── decorators/
│   └── interceptors/
├── repositories/
├── logics/
└── services/         # versioned HTTP/gRPC
```

Import direction: `configs ← models ← helpers ← adapters/repositories/logics/services`.

Live: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/

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

- Env vars override defaults; document keys in `.env.example`.
- Read with `BaseConfig.global_config()`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/config_management/

## Adapters (sketch)

```python
from archipy.adapters.redis.adapters import RedisAdapter

redis = RedisAdapter()  # uses global config.REDIS
```

Custom packages: `ports.py` (ABC) + `adapters.py` (+ optional `mocks.py`). Map client errors to domain errors with `raise ... from e`. Keep sync/async as separate classes.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/

## Utils

Prefer ArchiPy utils under `archipy.helpers.utils`:

| Util | Typical use |
|------|-------------|
| `TracingUtils` | tracing helpers |
| `RateLimitUtils` | rate limiting |
| `DatetimeUtils` | datetime helpers |
| `StringUtils` | string helpers |
| `JwtUtils` | JWT encode/decode |
| `PasswordUtils` | password hashing |
| `FileUtils` | file helpers |
| `ErrorUtils` | error helpers |
| `AppUtils` | app factories (e.g. FastAPI) |

Custom utils: pure only — no DB/network/adapter construction.

## Decorators

Prefer ArchiPy under `archipy.helpers.decorators`:

| Decorator area | Examples |
|----------------|----------|
| Cache | `ttl_cache` |
| Transactions | `sqlalchemy_atomic` / async variants |
| Observability | tracing, timing |
| Resilience | retry, timeout |
| Other | singleton, rate-limit |

No concrete adapter imports at module level in custom decorators.

## Interceptors

Prefer ArchiPy under `archipy.helpers.interceptors` (FastAPI / gRPC). Cross-cutting only (metrics, auth context, logging). Wire via DI or framework registration — not business logic.

Live helpers overview: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/

## Dependency injection

```bash
uv add "archipy[dependency-injection]"
```

Wire ports → adapters → repositories → logics in `configs/containers.py`. Override providers in tests.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/

## Errors

- Subclass ArchiPy domain/system/resource errors from `archipy.models.errors`.
- Raise with context: `raise NotFoundError(...) from e`.
- Do not leak raw driver exceptions into services.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/

## Quickstart path

1. `uv init` + `uv add "archipy[redis]"`
2. `AppConfig` + `set_global`
3. Use an ArchiPy adapter
4. Add logics/services as needed

Live: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

## API reference

https://syntaxarc.github.io/ArchiPy/api_reference/
