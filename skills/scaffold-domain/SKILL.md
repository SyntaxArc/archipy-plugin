---
name: scaffold-domain
description: >-
  Scaffold a full ArchiPy domain slice (DTOs, errors, repository + adapter, logic,
  service). Use for "add a <name> domain/module/feature", "new resource with CRUD", or
  "end-to-end endpoint".
---

# Scaffold ArchiPy Domain

## Read first

Read these plugin rules in full before generating files (paths relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../../rules/`):

- `../../rules/architecture-for-apps.mdc`
- `../../rules/using-archipy-models.mdc`
- `../../rules/using-archipy-repositories.mdc`
- `../../rules/using-archipy-logics.mdc`
- `../../rules/using-archipy-services.mdc`

## Before writing files

1. Inspect `pyproject.toml`, the package tree, neighboring domains, DI containers, and existing tests.
2. Infer package name, installed extras, naming, transport, and sync/async style from the repository.
3. Ask only for unresolved choices that materially change the generated slice:
   - Domain name
   - Missing infrastructure/extras
   - Transport when the app does not already establish one (default FastAPI)
4. Preserve existing files. Extend compatible modules; stop and explain conflicts instead of overwriting them.

## Compose — do not fork templates

Before generating files, read these plugin skills in full. Resolve `../...` paths relative to this `SKILL.md` file's
directory in the plugin installation (`$CURSOR_PLUGIN_ROOT/skills/scaffold-domain/` or
`${CLAUDE_SKILL_DIR}/`) — not relative to the app workspace:

- `../scaffold-models/SKILL.md`
- `../scaffold-adapter/SKILL.md`
- `../scaffold-logic/SKILL.md`
- `../scaffold-service/SKILL.md`

Apply their constraints and `Verify` sections in order; do not replace them with summaries:

1. **scaffold-models** — domain/repo DTOs, errors, optional entities
2. **scaffold-adapter** — thin wrapper under `repositories/<domain>/adapters/` + `<domain>_repository.py`
3. **scaffold-logic** — at least one use-case under `logics/<domain>/`
4. **scaffold-service** — `services/<domain>/v1/<domain>_service.py`

Install extras as needed: `uv add "archipy[<extras>]"`.

## Outcome checklist

- [ ] Domain + repository DTOs with ArchiPy naming (`*InputDTO`, `*CommandDTO`, …)
- [ ] Domain error subclassing ArchiPy `BaseError` hierarchy
- [ ] `repositories/<domain>/adapters/` + repository orchestrator
- [ ] One logic with `@postgres_sqlalchemy_atomic_decorator` when Postgres SQLAlchemy is in play
- [ ] One service v1 (FastAPI router or gRPC servicer)
- [ ] DI notes in `configs/containers.py`: ports → adapters → repository → logic → service

## Do not

- Call flow: `services → logics → repositories → adapters → ArchiPy`.
- Cross-domain: logics may call other logics; never another domain’s repository.
- Double quotes, Google-style docstrings, Python 3.14+ typing.
- Do **not** invent a top-level app `adapters/` package.
- No atomic / UoW decorators on repositories or services — only logics. There is no decorator named `atomic`.
- No FastAPI/gRPC imports in logics; no business rules in services/adapters.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Add or run Behave scenarios that exercise the new endpoints over REST/gRPC with their `@needs-*` containers
   (`/scaffold-bdd`), covering success, validation, and domain errors.
3. Confirm imports and DI wiring resolve without constructing production infrastructure.
4. Run the `archipy-reviewer` subagent on the changes and fix every **Must fix** finding it reports.
5. Report created/updated files, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
- Bundled: `../archipy-docs/reference.md`
