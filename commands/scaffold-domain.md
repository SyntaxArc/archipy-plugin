---
name: scaffold-domain
description: Scaffold a full ArchiPy domain slice (models, repo, logic, service)
---

# /scaffold-domain

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone, and do not replace the composed skills with summaries.

- `../skills/scaffold-archipy-domain/SKILL.md` (canonical workflow — follow it in full)
- `../skills/scaffold-archipy-models/SKILL.md`
- `../skills/scaffold-archipy-adapter/SKILL.md`
- `../skills/scaffold-archipy-logic/SKILL.md`
- `../skills/scaffold-archipy-service/SKILL.md`
- `../rules/architecture-for-apps.mdc` (call flow `services → logics → repositories → adapters → ArchiPy`)
- Layer rules as needed: `../rules/using-archipy-models.mdc`, `../rules/using-archipy-repositories.mdc`,
  `../rules/using-archipy-logics.mdc`, `../rules/using-archipy-services.mdc`

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: `pyproject.toml`, the package tree, neighboring domains, DI containers,
and existing tests. Infer package name, installed extras, naming, transport, and sync/async style from the repository.

## 2. Ask only for unresolved choices that materially change the slice

- Domain name
- Missing infrastructure/extras
- Transport when the app does not already establish one (default FastAPI)

Preserve existing files. Extend compatible modules; stop and explain conflicts instead of overwriting them.

## 3. Generate — compose, do not fork templates

Apply the composed skills' constraints and `Verify` sections in order:

1. **Models** — follow `../skills/scaffold-archipy-models/SKILL.md` (domain/repo DTOs, errors, optional entities).
   Do not invent DTO naming or inline a forked models template.
2. **Adapter** — thin wrapper under `repositories/<domain>/adapters/` + `<domain>_repository.py` orchestrator stub.
3. **Logic** — at least one use-case under `logics/<domain>/` with domain DTO I/O and
   `@postgres_sqlalchemy_atomic_decorator` (or async twin) when Postgres SQLAlchemy is in play.
4. **Service** — `services/<domain>/v1/<domain>_service.py` (FastAPI router or gRPC servicer).
5. Install extras as needed: `uv add "archipy[<extras>]"`.
6. Note DI wiring in `configs/containers.py`: ports → adapters → repository → logic → service.

## 4. Do not

- Do **not** invent a top-level app `adapters/` package.
- Cross-domain: logics may call other logics; never another domain's repository.
- No atomic / UoW decorators on repositories or services — only logics. There is no decorator named `atomic`.
- No FastAPI/gRPC imports in logics; no business rules in services/adapters.
- Double quotes, Google-style docstrings, Python 3.14+ typing.

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Run targeted domain tests; add a focused test when behavior, mapping, or error handling was added.
3. Confirm imports and DI wiring resolve without constructing production infrastructure.
4. Report created/updated files, dependency changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
