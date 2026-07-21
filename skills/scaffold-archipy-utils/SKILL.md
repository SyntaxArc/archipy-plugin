---
name: scaffold-archipy-utils
description: >-
  Scaffold or wire a helpers/utils module for an ArchiPy app. Prefer ArchiPy
  utils before inventing custom ones. Use when adding pure utility helpers.
---

# Scaffold ArchiPy Utils

## Scope

**Only** `helpers/utils/`. Do not create decorators or interceptors here.

## Before writing files

Ask:

1. Util name / purpose
2. Prefer existing ArchiPy util vs custom (`TracingUtils`, `RateLimitUtils`, `DatetimeUtils`, `StringUtils`, `JwtUtils`,
   `PasswordUtils`, `FileUtils`, `ErrorUtils`, `AppUtils`, …)

## Prefer ArchiPy

If an ArchiPy util fits, show import + usage example and stop — do not duplicate.

## Custom util

Create `helpers/utils/<name>_utils.py` (or similar):

- Pure functions/classes — no I/O, no DB, no adapters
- Google-style docstrings + full type hints
- Lazy-import optional deps inside functions when needed
- Brief usage snippet in the reply

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
- https://syntaxarc.github.io/ArchiPy/api_reference/
- Bundled skill reference: `../archipy-docs/reference.md` (Utils section)
