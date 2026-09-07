---
name: scaffold-observability
description: Configure ArchiPy 5.x OpenTelemetry traces, metrics, logs, and instrumentation
---

# /scaffold-observability

Read and follow the **scaffold-archipy-observability** skill in full. Inspect the workspace as directed there; ask only
for unresolved choices.

1. Install only the `otel*` extras matching the app stack.
2. Configure `BaseConfig.OTEL` through documented `OTEL__*` keys.
3. Initialize `OtelUtils` before DI constructs adapters, then use AppUtils/decorators for instrumentation.
4. Verify with test exporters; never commit OTLP credentials.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/observability/
