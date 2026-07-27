---
name: scaffold-archipy-domain
description: >-
  Scaffold a full ArchiPy domain slice (DTOs, errors, repository adapters,
  logic, service). Use when adding a new domain to an existing ArchiPy app.
---

# Scaffold ArchiPy Domain

## Before writing files

Ask the user for:

1. Domain name (e.g. `order`)
2. ArchiPy extras to install/use (e.g. `redis`, `postgres-sqlalchemy`, `fastapi`)
3. Transport: FastAPI (default) or gRPC

## Compose — do not fork templates

Apply existing skills in order (reuse their constraints and file layouts):

1. **Models** — `models/dtos/<domain>/domain/v1/` + `repository/` DTO stubs; `models/errors/<domain>_errors.py`;
   optional entity.
2. **scaffold-archipy-adapter** — thin wrapper under `repositories/<domain>/adapters/` + `<domain>_repository.py`.
3. **scaffold-archipy-logic** — at least one use-case under `logics/<domain>/`.
4. **scaffold-archipy-service** — `services/<domain>/v1/<domain>_service.py`.

Install extras as needed: `uv add "archipy[<extras>]"`.

## Outcome checklist

- [ ] Domain + repository DTOs with ArchiPy naming (`*InputDTO`, `*CommandDTO`, …)
- [ ] Domain error subclassing ArchiPy `BaseError` hierarchy
- [ ] `repositories/<domain>/adapters/` + repository orchestrator
- [ ] One logic with `@atomic` when Postgres SQLAlchemy is in play
- [ ] One service v1 (FastAPI router or gRPC servicer)
- [ ] DI notes in `configs/containers.py`: ports → adapters → repository → logic → service

## Constraints

- Call flow: `services → logics → repositories → adapters → ArchiPy`.
- Cross-domain: logics may call other logics; never another domain’s repository.
- Double quotes, Google-style docstrings, Python 3.14+ typing.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
