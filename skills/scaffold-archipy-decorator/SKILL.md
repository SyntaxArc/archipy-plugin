---
name: scaffold-archipy-decorator
description: >-
  Scaffold or wire a helpers/decorators module for an ArchiPy app. Prefer ArchiPy
  decorators (ttl_cache, sqlalchemy_atomic, tracing, …) before custom ones.
---

# Scaffold ArchiPy Decorator

## Scope

**Only** `helpers/decorators/`. Do not create utils or interceptors here.

## Before writing files

Ask:

1. Decorator purpose (cache, atomic, retry, timing, …)
2. Prefer ArchiPy built-in vs custom
3. Sync, async, or both

## Prefer ArchiPy

Examples:

- `from archipy.helpers.decorators.cache import ttl_cache`
- `from archipy.helpers.decorators.sqlalchemy_atomic import sqlalchemy_atomic_decorator`
- tracing / timeout / retry / singleton under `archipy.helpers.decorators`

Show correct usage on a sample function; do not reimplement.

## Custom decorator

Create `helpers/decorators/<name>.py`:

- Use `functools.wraps`
- Preserve types where practical
- Google-style docstring with Args/Returns and a usage example
- **No** concrete adapter imports at module level
- Separate sync/async wrappers if both needed

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- Bundled skill reference: `../archipy-docs/reference.md` (Decorators section)
