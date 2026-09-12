---
name: scaffold-bdd
description: Scaffold Behave BDD layout with ScenarioContext, pool manager, environment, optional testcontainers
---

# /scaffold-bdd

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-bdd/SKILL.md` (canonical workflow — follow it in full)
- `../rules/testing-bdd-for-apps.mdc` (Behave, ScenarioContext, `@needs-*` tags)

Copy skill templates from `reference/` resolved relative to the skill's `SKILL.md` location in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/scaffold-archipy-bdd/` or `$CLAUDE_PLUGIN_ROOT/skills/scaffold-archipy-bdd/`). These are
plugin templates, not app-relative paths. Copy and adapt them into the app; never edit the plugin copies.

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: existing `features/`, Behave config, scenario context, tags,
containers, and the behavior being tested. Infer naming and reuse shared support files.

## 2. Ask only for unresolved choices

- Feature name
- Mocks vs `@needs-*` infra (default mocks)

Never overwrite shared support files. Merge missing hooks/registrations while preserving project-specific behavior.

## 3. Generate

1. Install: `uv add "archipy[behave]"` (infra mode also `uv add "archipy[testcontainers]"`).
2. Always generate (if missing), modeled on ArchiPy `features/` (consumer-slim — no library gRPC/Temporal special
   cases unless the app needs them):
    - `features/scenario_context.py` (from `reference/scenario_context.py`)
    - `features/scenario_context_pool_manager.py` (from `reference/scenario_context_pool_manager.py`)
    - `features/test_helpers.py` (`get_current_scenario_context`, from `reference/test_helpers.py`)
    - `features/environment.py` (behave hooks + `TestConfig`, from `reference/environment.py`)
    - `features/<name>.feature` + `features/steps/<name>_steps.py`
3. Infra mode: also `features/test_containers.py` (`ContainerManager` + only needed containers — copy the pattern,
   not ArchiPy's full catalogue), `.env.test` image vars. Uncomment / wire `ContainerManager` in `environment.py`.
4. Gherkin is source of truth; tag infra `@needs-redis` / `@needs-postgres` / … Steps use
   `get_current_scenario_context(context)`; mocks mode injects mocks (e.g. `RedisMock`) — no Docker.

## 4. Do not

- Do **not** copy ArchiPy-core gRPC/Temporal server bootstrap unless the app tests those.
- Behave only (not pytest) as primary style.
- No shared mutable globals across scenarios; dispose context after each scenario.
- Do not paste ArchiPy's entire container catalogue or gRPC test servers.

## 5. Verify and report

1. Run the generated feature in mocks mode. Skip every `@needs-*` tag present
   (`uv run behave --tags=~@needs-redis --tags=~@needs-postgres` — a Redis-only skip still runs other infra).
2. For infra mode, run the narrow tagged scenario only when its required container runtime is available.
3. Confirm scenario context is isolated and disposed on both success and failure.
4. Report files, tags, dependency changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
