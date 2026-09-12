---
name: scaffold-observability
description: Configure ArchiPy 5.x OpenTelemetry traces, metrics, logs, and instrumentation
---

# /scaffold-observability

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-observability/SKILL.md` (canonical workflow — follow it in full)
- `../skills/archipy-docs/reference.md` (§ Observability — config keys, bootstrap order, decorators)
- `../rules/config-and-di.mdc` (global config before DI container construction)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: `pyproject.toml`/`uv.lock`, `AppConfig`, bootstrap order, app
transports, adapters, and `.env.example`. Infer required instrumentation extras from the installed stack.

## 2. Ask only for unresolved choices

- Enabled signals (traces / metrics / logs)
- OTLP endpoint/protocol, service name, sampling ratio, log level

Preserve existing config/bootstrap. Never write collector credentials or OTLP headers with secret values.

## 3. Generate

1. Install only the `otel*` extras matching the app stack (`otel`, `otel-fastapi`, `otel-grpc`, `otel-sqlalchemy`,
   `otel-redis`, `otel-elasticsearch`, `otel-kafka`, `otel-scylladb`, `otel-minio`), e.g.
   `uv add "archipy[otel-fastapi,otel-sqlalchemy,otel-redis]"`.
2. Configure `BaseConfig.OTEL` through documented non-secret `OTEL__*` defaults in `.env.example` (endpoint, protocol,
   service name, signals, exporters, sampling — see skill). ArchiPy builds providers programmatically; do not rely on
   SDK `OTEL_*` autoconfiguration.
3. Initialize before adapters — after `BaseConfig.set_global(config)`, before the DI container:
   `OtelUtils.init_otel_if_needed(config)` (from `archipy.helpers.utils.otel_utils`; idempotent, AppUtils re-calls
   safely). Early init matters for engines/clients/sessions created during bootstrap.
4. Instrument: FastAPI via `AppUtils.create_fastapi_app(config)`; gRPC server via `create_grpc_app` /
   `create_async_grpc_app`; gRPC clients via `OtelUtils.grpc_client_interceptors()` (+ async twin). Traces:
   `trace_root` / `trace_span` (+ async twins, `trace_class`); metrics: `measure_duration` / `count_calls` (+ async
   twins); exceptions via `BaseUtils.capture_exception`. Import decorators from `archipy.helpers.decorators`. Only
   capture non-sensitive argument names in trace attributes.

## 4. Do not

- Do not use removed ArchiPy 4.x extras/APIs: `prometheus`, `sentry`, `elastic-apm`, `TracingUtils`,
  `capture_transaction` / `capture_span` (use `trace_root` / `trace_span`), removed FastAPI rate-limit handler.
- Sync decorators reject coroutine functions — use async twins.
- Never commit OTLP credentials; no secrets in source, logs, or committed env files.

## 5. Verify and report

1. Run the repository formatter/linter and import the bootstrap without starting long-lived servers.
2. Confirm OTel initializes before adapter construction and AppUtils receives the same global/injected config.
3. Test with in-memory exporters or `OtelUtils.configure_for_testing`; do not require a production collector.
4. Confirm disabled signals no-op and no credentials appear in source, logs, or committed env files.
5. Report extras, config keys, bootstrap changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/observability/
