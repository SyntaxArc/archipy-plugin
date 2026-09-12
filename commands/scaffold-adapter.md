---
name: scaffold-adapter
description: Scaffold a domain adapter under repositories/{domain}/adapters/
---

# /scaffold-adapter

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-adapter/SKILL.md` (canonical workflow — follow it in full)
- `../rules/architecture-for-apps.mdc` (adapters sit behind repositories: `repositories → adapters → ArchiPy`)
- `../rules/using-archipy-adapters.mdc` (ports, mocks, boundary errors)
- `../rules/using-archipy-repositories.mdc` (repository orchestration)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: `pyproject.toml`, the target domain, neighboring adapters, ports, DI
wiring, and tests. Infer installed extras, naming, sync/async style, and existing ArchiPy integration.

## 2. Ask only for unresolved choices

- Domain and adapter purpose
- Sync or async when the repository does not establish one
- In-memory mock when testing requirements are unclear
- New external client when ArchiPy has no matching adapter

Preserve existing adapters and contracts. Extend compatible code; do not overwrite.

## 3. Generate

1. If ArchiPy already ships the client (Redis, Postgres, Kafka, …), prefer `uv add "archipy[<extra>]"` and a thin
   domain wrapper — not a full reimplementation.
2. Generate a thin wrapper under `repositories/<domain>/adapters/` (e.g. `user_db_adapter.py`): wrap the ArchiPy
   adapter (or external client), own entity construction / query building, map client errors → domain errors with
   `raise ... from e`.
3. Create `repositories/<domain>/<domain>_repository.py` stub if missing.
4. Optional mock: same module suffix or sibling file, only if BDD needs an in-memory double.
5. Ports: depend on ArchiPy ports when wrapping library adapters; add a local ABC only when the domain needs a custom
   contract. Wire via DI in `configs/containers.py`.

## 4. Do not

- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Never leak raw driver exceptions; always map with `raise ... from e`.

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Run focused adapter/repository tests with mocks; do not require live infrastructure unless the project already does.
3. Confirm imports, port conformance, exception chaining, and DI wiring.
4. Report files, dependency changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
