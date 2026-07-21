---
name: scaffold-archipy-interceptor
description: >-
  Scaffold or wire a helpers/interceptors module for an ArchiPy app. Prefer
  ArchiPy FastAPI/gRPC interceptors before custom ones. Cross-cutting only.
---

# Scaffold ArchiPy Interceptor

## Scope

**Only** `helpers/interceptors/`. Do not create utils or decorators here.

## Before writing files

Ask:

1. Framework: FastAPI, gRPC, or other
2. Sync or async
3. Prefer ArchiPy built-in vs custom
4. Cross-cutting concern (metrics, auth context, logging) — not a use-case

## Prefer ArchiPy

Check `archipy.helpers.interceptors` (FastAPI / gRPC). Show registration via DI or framework APIs from docs.

## Custom interceptor

Create under `helpers/interceptors/`:

- No domain business writes
- No adapter construction inside the interceptor module
- Wire through `configs/containers.py` or framework middleware registration
- Map errors at the boundary; do not leak raw exceptions

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- https://syntaxarc.github.io/ArchiPy/tutorials/observability/
- Bundled skill reference: `../archipy-docs/reference.md` (Interceptors section)
