---
name: redis-search
description: Scaffold Redis search adapters (RediSearch full-text, vector, search caching)
---

# /redis-search

Follow the **redis-search** skill.

1. Ask for search type (full-text / vector / caching), domain name, data structure, sync/async, and patterns needed.
2. Prefer `uv add "archipy[redis]"` and a thin domain wrapper under `repositories/<domain>/adapters/`.
3. Generate the matching adapter stub (s) + repository orchestrator stub if missing; wire via DI.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/ · bundled `skills/archipy-docs/reference.md`
