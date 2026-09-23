# ArchiPy Reference: Services and AppUtils bootstrap

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## AppUtils (FastAPI + gRPC)

```python
from archipy.helpers.utils.app_utils import AppUtils
from archipy.configs.base_config import BaseConfig

app = AppUtils.create_fastapi_app()              # config optional; reads global FASTAPI
server = AppUtils.create_grpc_app(BaseConfig.global_config())       # sync — config required
# server = AppUtils.create_async_grpc_app(config)                   # async
```

Do not hand-roll bare `FastAPI()` / `grpc.server()` when extras are installed. Prefer config flags for stock
middleware/interceptors (`OTEL.IS_ENABLED` / `OTEL.TRACES_ENABLED` / `OTEL.METRICS_ENABLED`,
`FASTAPI.GZIP_MIDDLEWARE_IS_ENABLED`, `GRPC_RATE_LIMIT.IS_ENABLED`). gRPC AppUtils installs traces and
`rpc.server.duration` metrics independently. Custom gRPC interceptors: `customized_interceptors=` on the gRPC
factories.
