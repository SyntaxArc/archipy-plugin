---
name: redis-search
description: Scaffold Redis search adapters (RediSearch full-text, vector, search caching)
---

# /redis-search

Read and follow the **redis-search** skill in full. Inspect the workspace as directed there; ask only for unresolved
choices.

1. Prefer `uv add "archipy[redis]"` and a thin domain wrapper under `repositories/<domain>/adapters/`.
2. Generate the matching adapter stub (s) + repository orchestrator stub if missing; wire via DI.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/ · bundled `skills/archipy-docs/reference.md`
