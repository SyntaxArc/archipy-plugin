# ArchiPy Reference: Configuration and dependency injection

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

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

ArchiPy 5.x does not ship FastAPI rate limiting; use `fastapi-redis-sdk` when needed. gRPC rate limiting remains
available through `GRPC_RATE_LIMIT.IS_ENABLED`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/config_management/

## Dependency injection

```bash
uv add "archipy[dependency-injection]"
```

Wire **ports → adapters → repositories → logics → services** in `configs/containers.py`. Override providers in tests.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/
