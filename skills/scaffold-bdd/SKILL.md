---
name: scaffold-bdd
description: >-
  Scaffold Behave BDD tests that drive an ArchiPy app through its REST/gRPC services layer against real
  testcontainers (Postgres, Redis, Kafka, Temporal, …). Use for "add tests", "acceptance/BDD/e2e tests",
  "behave", or "feature file".
---

# Scaffold ArchiPy BDD

## Read first

Read these plugin rules in full before generating files (paths relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../../rules/`):

- `../../rules/testing-bdd-for-apps.mdc`

## Before writing files

1. Inspect existing `features/`, Behave config, `.env.test`, tags, and the endpoints being tested.
2. Find the app's entrypoints: the `AppConfig` class, DI container, `create_<domain>_v{n}_router(container)` routers,
   `register_<domain>_v{n}_servicers(server, container)` for gRPC, Temporal workflows/activities, and how the schema is
   created (Alembic or `metadata.create_all`).
3. Derive the `@needs-*` tags from the infrastructure the endpoints touch (archipy extras in `pyproject.toml`, adapters
   under `repositories/*/adapters/`).
4. Ask only for an unresolved feature name. Never overwrite shared support files; merge missing hooks/containers while
   preserving project-specific behavior.

## Prefer ArchiPy

```bash
uv add --group dev "archipy[behave,testcontainers]"
```

FastAPI's `TestClient` needs nothing extra with `archipy[fastapi]`. gRPC tests need the app's generated stubs.

## Generate

Resolve files under `reference/` relative to this `SKILL.md` in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/scaffold-bdd/` or `${CLAUDE_SKILL_DIR}/`). These are
plugin templates, not app-relative paths. Copy and adapt them into the app; never edit the plugin copies.

**Copy templates from `reference/`, adapt package imports, create only if missing:**

| Destination                                 | Template                                     |
|---------------------------------------------|----------------------------------------------|
| `features/environment.py`                   | `reference/environment.py`                   |
| `features/test_containers.py`               | `reference/test_containers.py`               |
| `features/app_harness.py`                   | `reference/app_harness.py`                   |
| `features/scenario_context.py`              | `reference/scenario_context.py`              |
| `features/scenario_context_pool_manager.py` | `reference/scenario_context_pool_manager.py` |
| `features/test_helpers.py`                  | `reference/test_helpers.py`                  |
| `.env.test`                                 | `reference/env.test`                         |
| `features/<name>.feature` (pattern)         | `reference/example.feature`                  |
| `features/steps/<name>_steps.py` (pattern)  | `reference/example_steps.py`                 |

### Wire the harness (`features/app_harness.py`)

Fill every `ADAPT` hook; import app modules inside the hooks, never at module top:

- `build_rest_app()` — `AppUtils.create_fastapi_app()` + the same routers as `manage.create_app()`.
- `build_grpc_server()` — `AppUtils.create_grpc_app(config)` or `create_async_grpc_app(config)` +
  `register_<domain>_v{n}_servicers(server, container)`. No port binding; the harness binds `127.0.0.1:0`.
- `temporal_worker_spec()` — task queue, workflows, and activities of the app's worker.
- `prepare_state()` — schema once per run; `reset_state()` — wipe data between scenarios.

Return `None` from a hook the app does not need. Set `from configs.app_config import AppConfig` in `environment.py`
to the app's config class.

### Containers (`features/test_containers.py`)

The template registers Postgres, MySQL, Redis, Kafka, Temporal, MinIO, Elasticsearch, Keycloak, Vault, and ScyllaDB
with lazy imports, so unused ones cost nothing. Keep them all; `before_all` starts only the tags present in the run.
Pin images in `.env.test` when the app needs versions other than the defaults in `TestConfig`.

### Feature + steps

- Gherkin source of truth; tag each feature with every `@needs-*` service it touches.
- Steps use only `rest_client(context)`, `grpc_channel(context)` / `context.app.async_grpc_channel()`, and
  `get_current_scenario_context(context)` for per-scenario data.
- Cover success, validation errors, and domain errors as HTTP statuses / gRPC status codes produced by ArchiPy's
  handlers and interceptors.
- Third-party APIs with no container: override only that adapter provider with a port-conforming fake.

## Do not

- Behave only (not pytest) as primary style.
- Steps never call logics, repositories, adapters, or DI providers directly.
- Never create the test app without `AppUtils`, and never use `grpc_testing` or direct servicer calls.
- Do not mock databases, caches, queues, or Temporal — run their containers.
- No shared mutable globals across scenarios; `reset_state()` after each scenario.
- Do not stop or restart containers per feature — ArchiPy session managers bind once per run.

## Verify

1. Check Docker with `docker info`. If it is unavailable, say so and stop after a dry run
   (`uv run behave --dry-run`); do not fall back to mocks.
2. Run the new feature: `uv run behave features/<name>.feature`.
3. Confirm the scenarios pass in any order (data reset works) and containers stop at the end.
4. Report files, tags, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
