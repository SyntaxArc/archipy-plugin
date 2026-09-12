---
name: scaffold-logic
description: Scaffold an ArchiPy logic class with unit-of-work decorator
---

# /scaffold-logic

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-logic/SKILL.md` (canonical workflow — follow it in full)
- `../skills/scaffold-archipy-models/SKILL.md` (DTO/error stubs when missing)
- `../rules/architecture-for-apps.mdc` (logics own business rules + UoW)
- `../rules/using-archipy-logics.mdc` (DTO boundaries, atomic decorators, domain isolation)
- `../rules/using-archipy-models.mdc` (DTO naming when new DTO stubs are needed)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: the target domain's DTOs, repository contract, neighboring logics, DI
wiring, and tests. Infer naming and sync/async style from existing code and installed extras.

## 2. Ask only for unresolved choices

- Domain / use-case name
- Transaction choice (default sync for `postgres` + `sqlalchemy`, async for `postgres` + `sqlalchemy-async`)

Preserve existing use cases; do not overwrite logic or DTO files.

## 3. Generate

1. Install a SQLAlchemy extra only when this use-case owns a Postgres UoW:
   `uv add "archipy[postgres,sqlalchemy]"` or `uv add "archipy[postgres,sqlalchemy-async]"`. Skip for Redis/Kafka/other
   logics that do not wrap a SQLAlchemy session.
2. Generate `logics/<domain>/<name>_logic.py`:
   - Google-style class/method docstrings; double quotes; `X | Y` typing.
   - Constructor injects the domain repository (or port) — do not construct adapters.
   - Public method: domain `*InputDTO` in → domain `*OutputDTO` out.
   - Decorate with `postgres_sqlalchemy_atomic_decorator` or `async_postgres_sqlalchemy_atomic_decorator`
     (from `archipy.helpers.decorators.sqlalchemy_atomic`) **when Postgres SQLAlchemy is in play**. Otherwise omit the
     UoW decorator — there is no decorator named `atomic`.
3. If domain DTOs or errors are missing, follow `../skills/scaffold-archipy-models/SKILL.md` — do not invent naming.
4. Wire via DI in `configs/containers.py`.

## 4. Do not

- No FastAPI / gRPC imports in logics.
- May call other domain logics; **never** another domain's repository.
- No atomic / UoW decorators on repositories or services — only logics. There is no decorator named `atomic`.

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Add or run focused tests for success, business-rule failure, and rollback-relevant failure.
3. Confirm DTO boundaries, repository injection, decorator choice, and DI wiring.
4. Report files and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
