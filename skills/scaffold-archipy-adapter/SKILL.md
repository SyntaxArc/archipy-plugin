---
name: scaffold-archipy-adapter
description: >-
  Scaffold a domain adapter under repositories/{domain}/adapters/ for an ArchiPy
  app. Use when adding infrastructure integrations or thin wrappers around
  ArchiPy adapters.
---

# Scaffold ArchiPy Adapter

## Before writing files

Ask the user for:

1. Domain name (e.g. `user`, `order`)
2. Adapter purpose / file stem (e.g. `db`, `cache` → `user_db_adapter.py`)
3. Sync or async (or both as separate classes)
4. Whether an in-memory mock is needed for BDD
5. Whether this wraps an existing ArchiPy adapter or a new external client

## Prefer ArchiPy

If ArchiPy already ships the client (Redis, Postgres, Kafka, …), prefer:

```bash
uv add "archipy[<extra>]"
```

and a thin domain wrapper — not a full reimplementation.

## Generate

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_<purpose>_adapter.py   # e.g. user_db_adapter.py
└── <domain>_repository.py              # create stub if missing
```

- Thin wrapper: wrap ArchiPy adapter (or external client); own entity construction / query building; map client
  errors → domain errors with `raise ... from e`.
- Optional mock: same module suffix or sibling file only if BDD needs an in-memory double.
- Ports: depend on ArchiPy ports when wrapping library adapters; add a local ABC only when the domain needs a
  custom contract.

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Wire via DI in `configs/containers.py`.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
