---
name: scaffold-archipy-adapter
description: >-
  Scaffold a domain adapter under repositories/{domain}/adapters/ for an ArchiPy
  app. Use when adding infrastructure integrations or thin wrappers around
  ArchiPy adapters.
---

# Scaffold ArchiPy Adapter

## Before writing files

1. Inspect `pyproject.toml`, the target domain, neighboring adapters, ports, DI wiring, and tests.
2. Infer installed extras, naming, sync/async style, and existing ArchiPy integration.
3. Ask only for unresolved choices:
   - Domain and adapter purpose
   - Sync or async when the repository does not establish one
   - In-memory mock when testing requirements are unclear
   - New external client when ArchiPy has no matching adapter
4. Preserve existing adapters and contracts. Extend compatible code; do not overwrite.

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

- Thin wrapper: wrap ArchiPy adapter (or external client); own entity construction / query building; map client errors →
  domain errors with `raise ... from e`.
- Optional mock: same module suffix or sibling file only if BDD needs an in-memory double.
- Ports: depend on ArchiPy ports when wrapping library adapters; add a local ABC only when the domain needs a custom
  contract.

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Wire via DI in `configs/containers.py`.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Run focused adapter/repository tests with mocks; do not require live infrastructure unless the project already does.
3. Confirm imports, port conformance, exception chaining, and DI wiring.
4. Report files, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
