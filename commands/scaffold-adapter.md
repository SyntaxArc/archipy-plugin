---
name: scaffold-adapter
description: Scaffold a domain adapter under repositories/{domain}/adapters/
---

# /scaffold-adapter

Follow the **scaffold-archipy-adapter** skill.

1. Ask for domain name, adapter purpose, sync/async, and whether mocks are needed.
2. Prefer wrapping an existing ArchiPy adapter via extras when possible.
3. Generate a thin wrapper under `repositories/<domain>/adapters/` (e.g. `user_db_adapter.py`). Create
   `repositories/<domain>/<domain>_repository.py` stub if missing.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
