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
        self.UVICORN.RELOAD = self.ENVIRONMENT == EnvironmentType.LOCAL

config = AppConfig()
BaseConfig.set_global(config)  # auto-invokes customize()
```

- Env vars override defaults (`FASTAPI__SERVE_PORT`, …); document keys in `.env.example`.
- Read with `BaseConfig.global_config()`.

### FastAPIConfig + UvicornConfig

`config.FASTAPI` drives `AppUtils.create_fastapi_app` and the bind address; `config.UVICORN` (archipy >= 5.25.0) holds the
server settings and `AppUtils.uvicorn_config()` builds the `uvicorn.run` arguments — never hardcode host/port/reload.
The same names on `FASTAPI` are deprecated since 5.25.0:

| Area                | Fields                                                                    |
|---------------------|---------------------------------------------------------------------------|
| Bind (`FASTAPI`)    | `SERVE_HOST`, `SERVE_PORT`                                                |
| Server (`UVICORN`)  | `RELOAD`, `WORKERS_COUNT`, `TIMEOUT_KEEP_ALIVE`, `TIMEOUT_GRACEFUL_SHUTDOWN`, `WS_*` |
| Proxy (`UVICORN`)   | `PROXY_HEADERS`, `FORWARDED_ALLOW_IPS`                                    |
| TLS (`UVICORN`)     | `SSL_KEYFILE`, `SSL_CERTFILE` (together), `SSL_CA_CERTS`                  |
| App / docs (`FASTAPI`) | `PROJECT_NAME`, `OPENAPI_URL`, `DOCS_URL`, `RE_DOC_URL`                |

```python
config = BaseConfig.global_config()
uvicorn.run("manage:create_app", factory=True, **AppUtils.uvicorn_config(config))
# overrides: AppUtils.uvicorn_config(config, host="0.0.0.0", port=9000, reload=True)
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
