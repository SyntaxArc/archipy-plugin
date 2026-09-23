# ArchiPy Reference: Observability (OpenTelemetry)

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## Observability

Combine library pieces rather than inventing a parallel stack:

| Concern         | ArchiPy pieces                                                                                          | Extra                          |
|-----------------|---------------------------------------------------------------------------------------------------------|--------------------------------|
| Traces          | `OtelUtils`, `trace_root` / `trace_span` (+ async twins), AppUtils auto-instrumentation               | `otel` + `otel-fastapi`/`otel-grpc` |
| Metrics         | `measure_duration` / `count_calls` (+ async twins), AppUtils gRPC `rpc.server.duration`, `METRICS_EXPORTER` (`otlp`\|`pull`\|`pushgateway`) | `otel` (+ `otel-grpc` for RPC) |
| Logs            | `LOGS_EXPORTER` (`console`\|`otlp`); default console splits INFO/DEBUG → stdout, WARNING+ → stderr     | `otel`                         |
| Errors          | `BaseUtils.capture_exception` records on the current span                                               | `otel`                         |
| Timing only     | `timing_decorator`                                                                                      | —                              |

Configure through nested settings, not SDK autoconfiguration:

```bash
OTEL__IS_ENABLED=true
OTEL__SERVICE_NAME=my-service
OTEL__OTLP_ENDPOINT=http://localhost:4317
OTEL__PROTOCOL=grpc
OTEL__TRACES_ENABLED=true
OTEL__METRICS_ENABLED=true
OTEL__METRICS_EXPORTER=otlp
# Pull scrape (no collector): OTEL__METRICS_EXPORTER=pull
# Pushgateway: OTEL__METRICS_EXPORTER=pushgateway
# OTEL__METRICS_PUSHGATEWAY_URL=http://pushgateway.monitoring:9091
OTEL__METRICS_PULL_HOST=0.0.0.0
OTEL__METRICS_PULL_PORT=8200
OTEL__SYSTEM_METRICS_ENABLED=true
OTEL__LOGS_ENABLED=true
OTEL__LOGS_EXPORTER=console
OTEL__TRACES_SAMPLE_RATIO=0.1
OTEL__LOGS_LEVEL=WARNING
```

- Unique exporters: set `OTEL__METRICS_EXPORTER=pull` for scrape-only metrics on
  `METRICS_PULL_HOST:METRICS_PULL_PORT/metrics` (do not dual-export). Set
  `OTEL__METRICS_EXPORTER=pushgateway` plus `OTEL__METRICS_PUSHGATEWAY_URL` to push
  Prometheus text to a Pushgateway (no local scrape). `otlp` is OTLP to a collector,
  not Pushgateway. Set `OTEL__LOGS_EXPORTER=otlp` to push logs.
- If pull scrape cannot bind, ArchiPy logs a warning and keeps traces/logs/metrics.
- `OtelUtils.metrics_registry()` returns the Prometheus registry for `pull` / `pushgateway`.
- `SYSTEM_METRICS_ENABLED=false` disables process/system metrics when metrics are otherwise on.
- Prefer `WARNING` or higher for exported production logs when using OTLP.

Call `OtelUtils.init_otel_if_needed(config)` after `BaseConfig.set_global(config)` and **before** DI constructs
SQLAlchemy engines, Kafka clients, or ScyllaDB sessions. AppUtils repeats initialization safely and auto-instruments
FastAPI/gRPC when their matching extras are installed.

Health probes (above) are complementary but separate — probes answer infra routing; observability answers product/ops
insight. Use `/scaffold-observability` for a repository-aware setup.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/observability/
