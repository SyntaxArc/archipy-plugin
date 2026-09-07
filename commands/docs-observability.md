---
name: docs-observability
description: Open ArchiPy OpenTelemetry guidance (traces, metrics, logs)
---

# /docs-observability

Use the **archipy-docs** skill and the Observability section of `skills/archipy-docs/reference.md`.

Cover:

- OpenTelemetry: `BaseConfig.OTEL` + `OtelUtils`
- Tracing: `trace_root` / `trace_span` (+ async twins)
- Metrics: `measure_duration` / `count_calls` (+ async twins); `METRICS_EXPORTER` (`otlp`\|`pull`)
- Logs: `LOGS_EXPORTER` (`console`\|`otlp`); default console stream split
- AppUtils FastAPI instrumentation through `archipy[otel-fastapi]`
- AppUtils gRPC: contrib traces + ArchiPy `rpc.server.duration` metrics through `archipy[otel-grpc]`
  (metrics independent of traces)
- Timing: `timing_decorator`

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/interceptors/
