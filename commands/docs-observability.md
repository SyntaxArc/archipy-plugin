---
name: docs-observability
description: Open ArchiPy observability guidance (tracing, metrics, APM)
---

# /docs-observability

Use the **archipy-docs** skill and the Observability section of `skills/archipy-docs/reference.md`.

Cover:

- Tracing: `TracingUtils`, `capture_span` / `capture_transaction`
- Metrics: `PrometheusUtils`, metric interceptors (`archipy[prometheus]` required to import)
- APM / Sentry extras and AppUtils config flags
- Timing: `timing_decorator`

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/interceptors/
