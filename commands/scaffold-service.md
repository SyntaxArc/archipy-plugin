---
name: scaffold-service
description: Scaffold a thin ArchiPy FastAPI or gRPC service under services/{domain}/v{n}/
---

# /scaffold-service

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-service/SKILL.md` (canonical workflow — follow it in full)
- `../rules/architecture-for-apps.mdc` (services are thin transport, versioned `v{n}/`)
- `../rules/using-archipy-services.mdc` (AppUtils bootstrap, uvicorn via FastAPIConfig)
- `../rules/config-and-di.mdc` (uvicorn binds from `config.FASTAPI`)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: existing transports, domain DTOs/logics, app bootstrap, DI wiring, and
service tests. Infer domain, API version, framework, and sync/async style when established by the repository.

## 2. Ask only for unresolved choices

- Domain and logic to expose
- API version (default `v1`) and framework (default FastAPI) — only when no project convention exists

Preserve existing routes, servicers, and bootstrap code; integrate without overwriting.

## 3. Generate

1. Install transport extra: `uv add "archipy[fastapi]"` (HTTP) or `uv add "archipy[grpc]"` (gRPC).
2. Generate `services/<domain>/v{n}/<domain>_service.py` calling logic with domain DTOs:
   - **FastAPI:** thin router — request → domain `*InputDTO` → logic → `*OutputDTO`. Export
     `create_<domain>_v{n}_router(container)` for `manage.py` / app factory. Map domain errors to HTTP status.
   - **gRPC:** thin servicer calling logic; sync servicers with `AppUtils.create_grpc_app`, async with
     `create_async_grpc_app`.
3. Bootstrap via AppUtils — do not hand-roll bare `FastAPI()` / `grpc.server()`:
   `app = AppUtils.create_fastapi_app()` + `app.include_router(create_<domain>_v1_router(container))`.
4. uvicorn in `manage.py` from `config.FASTAPI` (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`,
   `FORWARDED_ALLOW_IPS`).

## 4. Do not

- No business rules / atomic UoW decorators in services.
- Do not mix sync/async servicer styles on one server.
- Version in path (`v1`, `v2`), not in business logic.
- Never hardcode host/port.
- Do not re-implement CORS/exception handlers/stock gRPC interceptors AppUtils already wires.
- Wire logic via DI container.

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Run focused transport tests without starting a long-lived server.
3. Confirm route/servicer registration, DTO mapping, domain-error mapping, and DI resolution.
4. Report files, dependency changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
