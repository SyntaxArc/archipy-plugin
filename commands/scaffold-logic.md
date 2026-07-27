---
name: scaffold-logic
description: Scaffold an ArchiPy logic class with unit-of-work decorator
---

# /scaffold-logic

Follow the **scaffold-archipy-logic** skill.

1. Ask for domain, logic name, and sync vs async atomic.
2. Generate `logics/<domain>/<name>_logic.py` with domain DTO I/O and `@postgres_sqlalchemy_atomic_decorator` (or async
   twin).
3. Inject repository via constructor; no FastAPI/gRPC imports.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
