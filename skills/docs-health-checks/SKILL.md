---
name: docs-health-checks
description: Open ArchiPy app health-check guidance for HTTP and gRPC liveness, readiness, startup probes, and shutdown
disable-model-invocation: true
---

# /docs-health-checks

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and `../archipy-docs/reference/health-checks.md`, plus bundled health-check
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
