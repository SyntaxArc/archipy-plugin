---
name: scaffold-observability
description: >-
  Configure ArchiPy 5.x OpenTelemetry traces, metrics, logs, and instrumentation. Use
  for "add tracing/metrics/OTel", "Prometheus/Pushgateway", or migrating off Sentry,
  Elastic APM, or old Prometheus.
---

# Scaffold ArchiPy OpenTelemetry

## Read first

Read these plugin rules in full before generating files (paths relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../../rules/`):

- `../../rules/config-and-di.mdc`

## Before writing files

1. Inspect `pyproject.toml`/`uv.lock`, `AppConfig`, bootstrap order, app transports, adapters, and `.env.example`.
2. Infer required instrumentation extras from the installed stack.
3. Ask only for unresolved choices: enabled signals, metrics exporter (`otlp` / `pull` /
   `pushgateway`), OTLP endpoint/protocol or Pushgateway URL, service name, sampling ratio,
   and log level.
4. Preserve existing config/bootstrap. Never write collector credentials or OTLP headers with secret values.

## Install only matching extras

| Stack | Extra |
|-------|-------|
| Core OTLP traces, metrics, logs | `otel` |
| FastAPI | `otel-fastapi` |
| gRPC | `otel-grpc` |
| SQLAlchemy | `otel-sqlalchemy` |
| Redis | `otel-redis` |
| Elasticsearch | `otel-elasticsearch` |
| Kafka | `otel-kafka` |
| ScyllaDB | `otel-scylladb` |
| MinIO/botocore | `otel-minio` |

Combine required extras, for example:

```bash
uv add "archipy[otel-fastapi,otel-sqlalchemy,otel-redis]"
```

Do not use removed ArchiPy 4.x extras: `prometheus`, `sentry`, or `elastic-apm`.

## Configure

Add non-secret defaults/documentation to `.env.example`:

```bash
OTEL__IS_ENABLED=true
OTEL__SERVICE_NAME=my-service
OTEL__OTLP_ENDPOINT=http://localhost:4317
OTEL__PROTOCOL=grpc
OTEL__TRACES_ENABLED=true
OTEL__METRICS_ENABLED=true
OTEL__METRICS_EXPORTER=otlp
# Pull scrape: OTEL__METRICS_EXPORTER=pull
# Pushgateway: OTEL__METRICS_EXPORTER=pushgateway
# OTEL__METRICS_PUSHGATEWAY_URL=http://pushgateway.monitoring:9091
OTEL__METRICS_PULL_HOST=0.0.0.0
OTEL__METRICS_PULL_PORT=8200
OTEL__SYSTEM_METRICS_ENABLED=true
OTEL__LOGS_ENABLED=true
OTEL__LOGS_EXPORTER=console
OTEL__TRACES_SAMPLE_RATIO=0.1
OTEL__LOGS_LEVEL=WARNING
OTEL__FASTAPI_EXCLUDED_URLS=health,docs,redoc,openapi.json
```

Use `BaseConfig.OTEL`; ArchiPy builds providers programmatically. Do not rely on OpenTelemetry SDK `OTEL_*`
autoconfiguration. For `http/protobuf`, use port 4318; ArchiPy appends `/v1/{signal}` when the base endpoint has no path.
Set `OTEL__METRICS_EXPORTER=pull` for scrape-only metrics. Set `OTEL__METRICS_EXPORTER=pushgateway`
and `OTEL__METRICS_PUSHGATEWAY_URL` (job defaults to `SERVICE_NAME`) for Prometheus Pushgateway —
no local `/metrics` server. `otlp` pushes OTLP to a collector; do not confuse it with Pushgateway.
If pull scrape cannot bind, ArchiPy logs a warning and keeps traces/logs/metrics providers.
Set `OTEL__LOGS_EXPORTER=otlp` to push logs to a collector (default `console` writes INFO/DEBUG to
stdout and WARNING+ to stderr).

## Initialize before adapters

After `BaseConfig.set_global(config)` and before constructing the DI container/adapters:

```python
from archipy.configs.base_config import BaseConfig
from archipy.helpers.utils.otel_utils import OtelUtils

config = AppConfig()
BaseConfig.set_global(config)
OtelUtils.init_otel_if_needed(config)
container = ApplicationContainer()
```

Initialization is idempotent. AppUtils calls it again safely. Early initialization matters for SQLAlchemy engines,
Kafka clients, ScyllaDB sessions, and logs created during bootstrap.

## Instrument application code

- FastAPI: `AppUtils.create_fastapi_app(config)` with `archipy[otel-fastapi]`.
- gRPC server: `create_grpc_app` / `create_async_grpc_app` with `archipy[otel-grpc]`.
  - Traces: contrib server interceptor when `OTEL.TRACES_ENABLED`.
  - Metrics: ArchiPy `GrpcServerOtelMetricsInterceptor` /
    `AsyncGrpcServerOtelMetricsInterceptor` records `rpc.server.duration` when
    `OTEL.METRICS_ENABLED` (works without traces).
- gRPC clients: `OtelUtils.grpc_client_interceptors()` / `async_grpc_client_interceptors()`.
- Traces: `trace_root`, `trace_span`, `async_trace_root`, `async_trace_span`, `trace_class`.
- Metrics: `measure_duration`, `async_measure_duration`, `count_calls`, `async_count_calls`.
- Exceptions: `BaseUtils.capture_exception` records on the current span.

Import decorators from `archipy.helpers.decorators`. Sync decorators reject coroutine functions; use their async twins.
Only capture non-sensitive argument names in trace attributes.

## ArchiPy 4.x migration

- `TracingUtils` → `OtelUtils`
- `capture_transaction` / `capture_span` → `trace_root` / `trace_span` (+ async twins)
- Prometheus/Sentry/Elastic APM config → `BaseConfig.OTEL`
- Removed FastAPI rate-limit handler → `fastapi-redis-sdk`

## Do not

- Never commit OTLP credentials; no secrets in source, logs, or committed env files.

## Verify

1. Run the repository formatter/linter and import the bootstrap without starting long-lived servers.
2. Confirm OTel initializes before adapter construction and AppUtils receives the same global/injected config.
3. Test with in-memory exporters or `OtelUtils.configure_for_testing`; do not require a production collector.
4. Confirm disabled signals no-op and no credentials appear in source, logs, or committed env files.
5. Run the `archipy-reviewer` subagent on the changes and fix every **Must fix** finding it reports.
6. Report extras, config keys, bootstrap changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/interceptors/
