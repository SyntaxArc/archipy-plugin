---
name: scaffold-service
description: Scaffold a thin ArchiPy FastAPI or gRPC service under services/{domain}/v{n}/
---

# /scaffold-service

Read and follow the **scaffold-archipy-service** skill in full. Inspect the workspace as directed there; ask only for
unresolved choices.

1. Generate `services/<domain>/v{n}/<domain>_service.py` calling logic with domain DTOs.
2. Bootstrap via `AppUtils`; uvicorn from `config.FASTAPI`.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
