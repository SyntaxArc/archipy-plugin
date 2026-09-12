---
name: scaffold-app
description: Scaffold a minimal ArchiPy application package layout
---

# /scaffold-app

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-app/SKILL.md` (canonical workflow — follow it in full)
- `../skills/scaffold-archipy-models/SKILL.md` (minimal DTO + error stubs)
- `../rules/architecture-for-apps.mdc` (layer map, call flow, import direction)
- `../rules/config-and-di.mdc` (BaseConfig, `customize()`, DI wiring)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: `pyproject.toml`, existing packages, config, and source layout.
Infer the package name and installed ArchiPy extras when they already exist.

## 2. Ask only for unresolved choices

- Python package name
- ArchiPy extras to install
- Optional first domain name (default `user`)

If files already exist, merge compatible additions and preserve project conventions.

## 3. Generate

1. Ensure the project uses `uv` and Python 3.14+: `uv add "archipy[<extras>]"`
2. Create the layout from the skill (`configs/`, `models/` with `dtos/<domain>/domain/v1/` + `repository/`, `entities/`,
   `errors/`, optional `helpers/` tree, `repositories/<domain>/` with `adapters/` + repository stub,
   `logics/<domain>/`, `services/<domain>/v1/`, `.env.example`, `manage.py` when FastAPI/HTTP requested,
   `features/` only via `/scaffold-bdd`).
3. Write `app_config.py` with `customize()` setting `self.FASTAPI.PROJECT_NAME` (and related defaults) plus
   `BaseConfig.set_global`.
4. Add a minimal domain DTO + error following `../skills/scaffold-archipy-models/SKILL.md`.
5. **When extras include `fastapi` (or user wants HTTP):** emit root `manage.py` where `create_app()` uses
   `AppUtils.create_fastapi_app()` and includes domain routers; `uvicorn.run` binds from `config.FASTAPI`
   (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`, `FORWARDED_ALLOW_IPS`).

## 4. Do not

- Never replace an existing application tree without explicit approval.
- No secrets in code; list env keys in `.env.example`.
- Never hardcode host/port; never hand-roll bare `FastAPI()` when AppUtils is in use.
- Do not invent a top-level app `adapters/` package — domain adapters live under `repositories/<domain>/adapters/`.
- There is no decorator named `atomic` — UoW means a real `*_sqlalchemy_atomic_decorator` on logics.
- Do not copy ArchiPy library maintainer tooling (graphify, library BDD internals).

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Import the package and app factory without starting network services.
3. Run existing targeted tests, if present.
4. Report created/updated files, installed extras, and commands run. Point the user to `/docs-quickstart` and
   `/scaffold-models` and `/scaffold-adapter` for DTOs and domain wrappers under
   `repositories/<domain>/adapters/`.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/
