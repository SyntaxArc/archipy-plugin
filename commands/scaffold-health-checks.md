---
name: scaffold-health-checks
description: Scaffold ArchiPy FastAPI and/or gRPC health checks and optional Kubernetes probe YAML
---

# /scaffold-health-checks

Follow the **scaffold-archipy-health-checks** skill.

1. Ask for package name, transport (FastAPI / gRPC / both), readiness dependencies, optional heartbeat liveness, and
   optional K8s probe YAML.
2. Generate shared check helpers plus:
    - FastAPI: `services/health/v1/health_service.py` (`/health/live`, `/health/ready`)
    - gRPC: `services/health/v1/health_grpc_service.py` (`grpc.health.v1` with `liveness` / `readiness` service names)
3. Wire via `AppUtils.create_fastapi_app()` / `create_grpc_app` / `create_async_grpc_app`; emit `deploy/k8s-probes.yaml`
   when requested (`httpGet` and/or `grpc` probes).

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
