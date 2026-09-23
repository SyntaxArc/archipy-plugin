---
name: docs-errors
description: Open ArchiPy error-handling guidance
disable-model-invocation: true
---

# /docs-errors

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and the Errors section of `../archipy-docs/reference.md`.

Cover:

- Subclassing ArchiPy `BaseError` hierarchy
- `raise ... from e` and never bare `Exception` for domain failures
- Mapping driver errors at adapter boundaries
- FastAPI status mapping when using `AppUtils` exception handlers

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/

Offer `/scaffold-models` if they want DTO or error modules generated.
