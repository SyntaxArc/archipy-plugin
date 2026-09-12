---
name: docs-health-checks
description: Open ArchiPy app health-check guidance for HTTP and gRPC liveness, readiness, startup probes, and shutdown
---

# /docs-health-checks

Read `../skills/archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this
command file inside the plugin installation) — via `../skills/archipy-docs/reference.md`, plus bundled health-check
guidance.

Cover:

- Liveness vs readiness vs startup probes
- FastAPI `/health/live` and `/health/ready` route design
- gRPC `grpc.health.v1.Health` with `liveness` / `readiness` / empty service names
- Kubernetes `httpGet` and `grpc` probe defaults and drain behavior
- Common mistakes: dependency checks in liveness, missing timeouts, custom gRPC health RPCs instead of the standard
  protocol

Next step: suggest `/scaffold-health-checks` when the user wants concrete FastAPI routes, gRPC Health servicer wiring,
or K8s probe YAML.
