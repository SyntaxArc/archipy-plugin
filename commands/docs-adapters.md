---
name: docs-adapters
description: Open ArchiPy adapter patterns and API docs for app teams
---

# /docs-adapters

Use the **archipy-docs** skill and the Adapters section of `skills/archipy-docs/reference.md`.

Cover:

- Prefer ArchiPy extras + shipped adapters
- Domain wrappers under `repositories/{domain}/adapters/` (e.g. `user_db_adapter.py`)
- Boundary error mapping (`raise ... from e`)

Live docs:

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/

Offer `/scaffold-adapter` if they want files generated.
