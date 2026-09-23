# ArchiPy Reference: Helpers: utils, decorators, interceptors

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## Utils

Prefer ArchiPy utils. Import from the **concrete submodule** (package `__init__` does not re-export):

| Util              | Import path                              | Typical use                     |
|-------------------|------------------------------------------|---------------------------------|
| `AppUtils`        | `archipy.helpers.utils.app_utils`        | FastAPI / gRPC app factories    |
| `BaseUtils`       | `archipy.helpers.utils.base_utils`       | Shared facade helpers           |
| `OtelUtils`       | `archipy.helpers.utils.otel_utils`       | OpenTelemetry provider lifecycle |
| `RateLimitUtils`  | `archipy.helpers.utils.rate_limit_utils` | rate limiting                   |
| `DatetimeUtils`   | `archipy.helpers.utils.datetime_utils`   | datetime helpers                |
| `StringUtils`     | `archipy.helpers.utils.string_utils`     | string helpers                  |
| `JWTUtils`        | `archipy.helpers.utils.jwt_utils`        | JWT encode/decode (`jwt` extra) |
| `PasswordUtils`   | `archipy.helpers.utils.password_utils`   | password hashing                |
| `FileUtils`       | `archipy.helpers.utils.file_utils`       | file helpers                    |
| `ErrorUtils`      | `archipy.helpers.utils.error_utils`      | error helpers                   |
| `TOTPUtils`       | `archipy.helpers.utils.totp_utils`       | TOTP                            |
| `KeycloakUtils`   | `archipy.helpers.utils.keycloak_utils`   | Keycloak helpers                |

Custom utils: pure only — no DB/network/adapter construction.

## Decorators

Prefer ArchiPy under `archipy.helpers.decorators`:

| Area                         | Symbols                                                                                                                   |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Cache                        | `ttl_cache_decorator` (`archipy.helpers.decorators.cache`)                                                                |
| Transactions (on **logics**) | `postgres_sqlalchemy_atomic_decorator`, `async_postgres_sqlalchemy_atomic_decorator`, plus sqlite/starrocks/generic twins |
| Observability                | `trace_span`, `trace_root`, `async_trace_span`, `async_trace_root`, `trace_class`; `timing_decorator`                    |
| Metrics                      | `measure_duration`, `async_measure_duration`, `count_calls`, `async_count_calls`                                        |
| Resilience                   | `retry_decorator`, `timeout_decorator`                                                                                    |
| Other                        | `singleton_decorator`, `grpc_rate_limit_decorator` (gRPC only)                                                            |

No concrete adapter imports at module level in custom decorators.

## Interceptors

Prefer ArchiPy under `archipy.helpers.interceptors` (FastAPI / gRPC). Cross-cutting only. Prefer AppUtils
auto-registration for stock hooks; wire custom via DI / `customized_interceptors=` — not business logic.

### Instrumentation and rate limiting

- FastAPI: `AppUtils.create_fastapi_app` auto-instruments through `archipy[otel-fastapi]` when `OTEL.IS_ENABLED`.
- gRPC traces: AppUtils factories insert the contrib OTel server interceptor through `archipy[otel-grpc]` when
  `OTEL.TRACES_ENABLED`.
- gRPC metrics: AppUtils also prepends ArchiPy `GrpcServerOtelMetricsInterceptor` /
  `AsyncGrpcServerOtelMetricsInterceptor` (`rpc.server.duration`) when `OTEL.METRICS_ENABLED` — independent of
  traces.
- gRPC rate-limit: `GRPC_RATE_LIMIT.IS_ENABLED` + `grpc_rate_limit_decorator` / stock interceptors.
- FastAPI rate-limit handlers were removed in 5.0; use `fastapi-redis-sdk`.

Live helpers overview: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
