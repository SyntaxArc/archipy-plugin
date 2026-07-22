---
name: docs-errors
description: Open ArchiPy error-handling guidance
---

# /docs-errors

Use the **archipy-docs** skill and the Errors section of `skills/archipy-docs/reference.md`.

Cover:

- Subclassing ArchiPy `BaseError` hierarchy
- `raise ... from e` and never bare `Exception` for domain failures
- Mapping driver errors at adapter boundaries
- FastAPI status mapping when using `AppUtils` exception handlers

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/
