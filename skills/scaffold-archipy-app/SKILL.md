---
name: scaffold-archipy-app
description: >-
  Scaffold a minimal ArchiPy application package (config, containers stub, domain
  slice, helpers tree, optional manage.py). Use when starting a new ArchiPy-based
  service or asking to bootstrap project layout.
---

# Scaffold ArchiPy App

## Before writing files

Ask the user for:

1. Python package name (e.g. `my_app`)
2. ArchiPy extras to install (e.g. `redis`, `dependency-injection`, `postgres-sqlalchemy`, `fastapi`)
3. Optional: first domain name (default `user`)

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

4. Write `app_config.py` with `customize()` setting `self.FASTAPI.PROJECT_NAME` (and related defaults) + `BaseConfig.set_global`.
5. Add a minimal domain DTO + error subclassing ArchiPy base errors.
6. **When extras include `fastapi` (or user wants HTTP):** emit root `manage.py`:
   - `create_app()` uses `AppUtils.create_fastapi_app()` and includes domain routers.
   - `uvicorn.run` binds from `config.FASTAPI` (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`, `FORWARDED_ALLOW_IPS`) — never hardcode host/port.
7. Document next steps: `/scaffold-domain`, `/scaffold-adapter`, `/scaffold-bdd`, `/docs-quickstart`.

## Constraints

- Double quotes, Google-style docstrings, `X | Y` typing.
- No secrets in code; list env keys in `.env.example`.
- Do not copy ArchiPy library maintainer tooling (graphify, library BDD internals).

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
