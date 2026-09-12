---
name: scaffold-health-checks
description: Scaffold ArchiPy FastAPI and/or gRPC health checks and optional Kubernetes probe YAML
---

# /scaffold-health-checks

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-health-checks/SKILL.md` (canonical workflow — follow it in full)
- `../skills/archipy-docs/reference.md` (§ Health checks — probe semantics, endpoint sketches, gRPC protocol,
  K8s rules, graceful shutdown; source of truth, do not invent alternate meanings)
- `../rules/using-archipy-services.mdc` (thin transport, AppUtils bootstrap)

Copy skill templates from `reference/` resolved relative to the skill's `SKILL.md` location in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/scaffold-archipy-health-checks/` or
`$CLAUDE_PLUGIN_ROOT/skills/scaffold-archipy-health-checks/`). Copy and adapt them into the app; never edit the
plugin copies.

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: package/config, current transports, app lifecycle, dependency adapters,
DI wiring, deployment manifests, and existing health endpoints. Infer package name, transport, ports, and readiness
dependencies from the repository.

## 2. Ask only for unresolved choices

- Transport: FastAPI / gRPC / both
- Readiness dependencies to include
- Optional heartbeat liveness (deadlock detection — only when asked)
- Optional Kubernetes probe YAML

Preserve existing health routes and manifests; merge compatible additions instead of overwriting.

## 3. Generate

1. Install: `uv add "archipy[fastapi]"` (HTTP) and/or `uv add "archipy[grpc]"` (gRPC server +
   grpcio-health-checking).
2. Generate shared check helpers plus, per transport:
   - FastAPI: `<package>/services/health/v1/health_service.py` — thin router for `GET /health/live` and
     `GET /health/ready` (`200` healthy, `503` not ready). Liveness = process-only, no deps. Readiness = deps +
     warm-up + shutdown, timeouts, per-check detail. Wire with `include_router` into `manage.py` / app factory.
   - gRPC: `<package>/services/health/v1/health_grpc_service.py` — standard `grpc.health.v1.Health` protocol via
     `grpcio-health-checking`. Register at least `""` (overall), `"readiness"`, `"liveness"`; ready/alive →
     `SERVING`, not ready → `NOT_SERVING`. `""` and `"readiness"` start `NOT_SERVING` until warm-up + deps healthy;
     never flip `"liveness"` for dep failures. Prefer background updater calling `set()`; on `SIGTERM` set
     readiness/`""` to `NOT_SERVING`, then `enter_graceful_shutdown()`.
3. Bootstrap via AppUtils (`create_fastapi_app` / `create_grpc_app` / `create_async_grpc_app`); never hand-roll bare
   `FastAPI()` / `grpc.server()`. Never mix sync and async gRPC servicer styles on one server.
4. Startup probes: HTTP → `/health/live`; gRPC → service `"liveness"` (prefer over `""`).
5. K8s YAML when requested: `deploy/k8s-probes.yaml` matching chosen transport(s) (copy
   `reference/k8s-probes-http.yaml` / `reference/k8s-probes-grpc.yaml`, adapt ports to
   `config.GRPC.SERVE_PORT` / `config.FASTAPI.SERVE_PORT`). Rules: `readinessProbe.successThreshold: 2`,
   `failureThreshold: 3` default, `timeoutSeconds` ≥ slowest readiness check timeout, `preStop` sleep drain window.

## 4. Do not

- Keep services thin; no business rules in health transport.
- Never hardcode ports in app code (YAML may show placeholders matching config).
- No warm-up/shutdown-blind readiness; no dependency checks in liveness; no custom gRPC health RPCs — use the
  standard protocol.
- No secrets in code; double quotes, Google-style docstrings, `X | Y` typing.

## 5. Verify and report

1. Run formatter/linter and focused health tests without starting a long-lived server: healthy, dependency failure,
   timeout, warm-up, and shutdown states (take down a dependency to test failure behavior).
2. Validate generated Kubernetes YAML; confirm probe ports/paths/service names match app config.
3. Report files, dependencies, and commands run. Suggest `/docs-health-checks` for explanation and
   `/docs-observability` for metrics/tracing follow-up.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
