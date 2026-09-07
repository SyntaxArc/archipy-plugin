---
name: scaffold-archipy-bdd
description: >-
  Scaffold Behave BDD layout for an ArchiPy app (feature, steps, ScenarioContext,
  pool manager, environment, optional testcontainers). Use when adding acceptance
  tests under features/.
---

# Scaffold ArchiPy BDD

## Before writing files

1. Inspect existing `features/`, Behave config, scenario context, tags, containers, and the behavior being tested.
2. Infer naming and reuse shared support files. Ask only for an unresolved feature name or whether real infrastructure is
   required; default to mocks.
3. Never overwrite shared support files. Merge missing hooks/registrations while preserving project-specific behavior.

## Prefer ArchiPy

```bash
uv add "archipy[behave]"
# infra mode also:
uv add "archipy[testcontainers]"
```

## Generate

Under **project root** (create shared files only if missing):

```text
features/
├── <name>.feature
├── steps/
│   └── <name>_steps.py
├── scenario_context.py              # always — adapt from ArchiPy pattern
├── scenario_context_pool_manager.py # always — Singleton pool
├── environment.py                   # always — behave hooks
├── test_helpers.py                  # always — get_current_scenario_context
└── test_containers.py               # infra mode only — ContainerManager + needed containers
.env.test                            # infra mode — REDIS__IMAGE, POSTGRES__IMAGE, …
```

Model after ArchiPy `features/` + docs tutorial (consumer-slim — no library gRPC/Temporal special cases unless the app
needs them).

Resolve files under `reference/` relative to this `SKILL.md` in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/scaffold-archipy-bdd/` or `$CLAUDE_PLUGIN_ROOT/skills/scaffold-archipy-bdd/`). These are
plugin templates, not app-relative paths. Copy and adapt them into the app; never edit the plugin copies.

**Copy templates from `reference/`, adapt package imports, create only if missing:**

| Destination                                 | Template                                     |
|---------------------------------------------|----------------------------------------------|
| `features/scenario_context.py`              | `reference/scenario_context.py`              |
| `features/scenario_context_pool_manager.py` | `reference/scenario_context_pool_manager.py` |
| `features/test_helpers.py`                  | `reference/test_helpers.py`                  |
| `features/environment.py`                   | `reference/environment.py`                   |

Uncomment / wire `ContainerManager` in `environment.py` when mode is infra.

### `features/test_containers.py` (infra mode)

Copy **pattern** from ArchiPy `features/test_containers.py`, not the full multi-service registry:

1. `TAG_CONTAINER_MAP` (`needs-redis` → `redis`, …)
2. `ContainerManager` with `register`, `get_container`, `start_containers`, `extract_containers_from_tags`, `stop_all`
3. Only register containers the app actually tests (e.g. one `RedisTestContainer` Singleton that starts
   `RedisContainer`, patches `BaseConfig.global_config().REDIS`)

Do **not** paste ArchiPy’s entire container catalogue or gRPC test servers.

### Feature + steps

- Gherkin source of truth; tag infra `@needs-redis` / `@needs-postgres` / …
- Steps: `get_current_scenario_context(context)` or `context.scenario_context_pool.get_context(context.scenario.id)`
- Mocks mode: inject `RedisMock` into scenario context — no Docker
- Skip infra: `uv run behave --tags=~@needs-redis`

## Constraints

- Behave only (not pytest) as primary style.
- No shared mutable globals across scenarios.
- Dispose context after each scenario; `stop_all` after feature/all when using containers.
- Consumer apps: slim templates — library `environment.py` gRPC/Temporal blocks are ArchiPy-core specific.

## Verify

1. Run the generated feature in mocks mode.
2. For infra mode, run the narrow tagged scenario only when its required container runtime is available.
3. Confirm scenario context is isolated and disposed on both success and failure.
4. Report files, tags, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
