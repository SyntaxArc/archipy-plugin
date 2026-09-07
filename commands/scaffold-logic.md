---
name: scaffold-logic
description: Scaffold an ArchiPy logic class with unit-of-work decorator
---

# /scaffold-logic

Read and follow the **scaffold-archipy-logic** skill in full. Inspect the workspace as directed there; ask only for
unresolved choices.

1. Generate `logics/<domain>/<name>_logic.py` with domain DTO I/O and `@postgres_sqlalchemy_atomic_decorator` (or async
   twin).
2. Inject repository via constructor; no FastAPI/gRPC imports.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
