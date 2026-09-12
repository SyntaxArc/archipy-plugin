---
name: docs-errors
description: Open ArchiPy error-handling guidance
---

# /docs-errors

Read `../skills/archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this
command file inside the plugin installation) — and the Errors section of `../skills/archipy-docs/reference.md`.

Cover:

- Subclassing ArchiPy `BaseError` hierarchy
- `raise ... from e` and never bare `Exception` for domain failures
- Mapping driver errors at adapter boundaries
- FastAPI status mapping when using `AppUtils` exception handlers

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/

Offer `/scaffold-models` if they want DTO or error modules generated.
