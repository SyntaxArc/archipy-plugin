---
name: scaffold-adapter
description: Scaffold a custom ArchiPy-style adapter (ports, adapters, optional mocks)
---

# /scaffold-adapter

Follow the **scaffold-archipy-adapter** skill.

1. Ask for service name, sync/async, and whether mocks are needed.
2. Prefer wrapping an existing ArchiPy adapter via extras when possible.
3. Generate `ports.py`, `adapters.py`, and optional `mocks.py` under `adapters/<name>/`.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
