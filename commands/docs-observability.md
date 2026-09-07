---
name: docs-observability
description: Open ArchiPy OpenTelemetry guidance (traces, metrics, logs)
---

# /docs-observability

Use the **archipy-docs** skill and the Observability section of `skills/archipy-docs/reference.md`.

Cover:

- OpenTelemetry: `BaseConfig.OTEL` + `OtelUtils`
- Tracing: `trace_root` / `trace_span` (+ async twins)
- Metrics: `measure_duration` / `count_calls` (+ async twins)
- AppUtils instrumentation through `archipy[otel-fastapi]` / `archipy[otel-grpc]`
- Timing: `timing_decorator`

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/interceptors/
