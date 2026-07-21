---
name: scaffold-archipy-adapter
description: >-
  Scaffold a custom adapter package (ports.py, adapters.py, optional mocks.py)
  for an ArchiPy app. Use when adding infrastructure integrations or domain
  wrappers around ArchiPy adapters.
---

# Scaffold ArchiPy Adapter

## Before writing files

Ask the user for:

1. Service / adapter name (e.g. `payments`, `user_cache`)
2. Sync or async (or both as separate classes)
3. Whether an in-memory `mocks.py` is needed for BDD
4. Whether this wraps an existing ArchiPy adapter or a new external client

## Prefer ArchiPy

If ArchiPy already ships the client (Redis, Postgres, Kafka, …), prefer:

```bash
uv add "archipy[<extra>]"
```

and a thin domain wrapper — not a full reimplementation.

## Generate

```text
adapters/<name>/
├── __init__.py
├── ports.py
├── adapters.py
└── mocks.py          # only if requested / needed for BDD
```

- `ports.py`: ABC with abstract methods and full type hints.
- `adapters.py`: concrete class; read config from `BaseConfig.global_config()` or constructor injection; map client errors → domain errors with `raise ... from e`.
- `mocks.py`: in-memory implementation of the same port (optional).

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Export the port from `__init__.py` for DI wiring.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
