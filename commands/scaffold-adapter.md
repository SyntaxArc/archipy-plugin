---
name: scaffold-adapter
description: Scaffold a domain adapter under repositories/{domain}/adapters/
---

# /scaffold-adapter

Read and follow the **scaffold-archipy-adapter** skill in full. Inspect the workspace as directed there; ask only for
unresolved choices.

1. Prefer wrapping an existing ArchiPy adapter via extras when possible.
2. Generate a thin wrapper under `repositories/<domain>/adapters/` (e.g. `user_db_adapter.py`). Create
   `repositories/<domain>/<domain>_repository.py` stub if missing.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
