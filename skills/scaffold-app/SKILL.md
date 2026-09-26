---
name: scaffold-app
description: >-
  Bootstrap a new ArchiPy service layout (configs, models, repositories, logics,
  services, helpers, manage.py). Use for "new service/project", "start an archipy app",
  or "set up the project structure".
---

# Scaffold ArchiPy App

## Read first

Read these plugin rules in full before generating files (paths relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../../rules/`):

- `../../rules/architecture-for-apps.mdc`
- `../../rules/config-and-di.mdc`

## Before writing files

1. Inspect the workspace for `pyproject.toml`, existing packages, config, and source layout.
2. Infer the package name and installed extras when they already exist.
3. Ask only for unresolved choices:
   - Python package name
   - ArchiPy extras to install
   - Optional first domain name (default `user`)
4. If files already exist, merge compatible additions and preserve project conventions. Never replace an existing
   application tree without explicit approval.

## Steps

1. Ensure project uses `uv` and Python 3.14+.
2. Install: `uv add "archipy[<extras>]"`
3. Create layout:

```text
<package>/
├── configs/
│   ├── __init__.py
│   ├── app_config.py      # AppConfig(BaseConfig) + set_global
│   └── containers.py      # DI stub (if dependency-injection extra)
├── models/
│   ├── __init__.py
│   ├── dtos/<domain>/
│   │   ├── domain/v1/
│   │   └── repository/
│   ├── entities/
│   └── errors/
├── helpers/               # optional — prefer archipy.helpers first
│   ├── __init__.py
│   ├── utils/__init__.py
│   ├── decorators/__init__.py
│   └── interceptors/__init__.py
├── repositories/
│   └── <domain>/
│       ├── adapters/
│       └── <domain>_repository.py
├── logics/
│   └── <domain>/
└── services/
    └── <domain>/v1/
manage.py                  # when fastapi (or HTTP) requested
features/                  # optional — /scaffold-bdd
.env.example
```

4. Write `app_config.py` with `customize()` setting `self.FASTAPI.PROJECT_NAME` (and related defaults) +
   `BaseConfig.set_global`.
5. Add a minimal domain DTO + error following `../scaffold-models/SKILL.md`.
6. **When extras include `fastapi` (or user wants HTTP):** emit root `manage.py`:
    - `create_app()` uses `AppUtils.create_fastapi_app()` and includes domain routers.
    - `uvicorn.run` binds from `config.FASTAPI` (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`,
      `FORWARDED_ALLOW_IPS`) — never hardcode host/port.
7. Document next steps: `/scaffold-domain`, `/scaffold-models`, `/scaffold-adapter`, `/scaffold-bdd`,
   `/scaffold-health-checks`, `/docs-quickstart`.

## Do not

- Double quotes, Google-style docstrings, `X | Y` typing.
- No secrets in code; list env keys in `.env.example`.
- Do not copy ArchiPy library maintainer tooling (library BDD internals).
- Never hardcode host/port; never hand-roll bare `FastAPI()` when AppUtils is in use.
- Do not invent a top-level app `adapters/` package — domain adapters live under `repositories/<domain>/adapters/`.
- There is no decorator named `atomic` — UoW means a real `*_sqlalchemy_atomic_decorator` on logics.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Import the package and app factory without starting network services.
3. Run existing targeted tests, if present.
4. Run the `archipy-reviewer` subagent on the changes and fix every **Must fix** finding it reports.
5. Report created/updated files, installed extras, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
