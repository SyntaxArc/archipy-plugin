---
name: scaffold-archipy-app
description: >-
  Scaffold a minimal ArchiPy application package (config, containers stub, domain
  slice, helpers tree). Use when starting a new ArchiPy-based service or asking
  to bootstrap project layout.
---

# Scaffold ArchiPy App

## Before writing files

Ask the user for:

1. Python package name (e.g. `my_app`)
2. ArchiPy extras to install (e.g. `redis`, `dependency-injection`, `postgres-sqlalchemy`)
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
│   ├── dtos/<domain>/domain/v1/
│   ├── entities/
│   └── errors/
├── adapters/
│   └── __init__.py
├── helpers/
│   ├── __init__.py
│   ├── utils/__init__.py
│   ├── decorators/__init__.py
│   └── interceptors/__init__.py
├── repositories/
├── logics/
└── services/
features/                  # optional BDD stub note
.env.example
```

4. Write `app_config.py` following ArchiPy quickstart (`customize()`, `BaseConfig.set_global`).
5. Add a minimal domain DTO + error subclassing ArchiPy base errors.
6. Document next steps: `/scaffold-adapter`, wire Redis/Postgres, `/docs-quickstart`.

## Constraints

- Double quotes, Google-style docstrings, `X | Y` typing.
- No secrets in code; list env keys in `.env.example`.
- Do not copy ArchiPy library maintainer tooling (graphify, library BDD internals).

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
