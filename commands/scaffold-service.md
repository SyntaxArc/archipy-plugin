---
name: scaffold-service
description: Scaffold a thin ArchiPy FastAPI or gRPC service under services/{domain}/v{n}/
---

# /scaffold-service

Follow the **scaffold-archipy-service** skill.

1. Ask for domain, API version, and FastAPI vs gRPC (sync/async).
2. Generate `services/<domain>/v{n}/<domain>_service.py` calling logic with domain DTOs.
3. Bootstrap via `AppUtils`; uvicorn from `config.FASTAPI`.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
