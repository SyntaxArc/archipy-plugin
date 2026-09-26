---
name: docs-testing
description: Open ArchiPy BDD testing guidance
disable-model-invocation: true
---

# /docs-testing

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and `../archipy-docs/reference/testing.md`.

Cover:

- Behave layout (`features/`, steps, ScenarioContext, app harness)
- Scenarios through the services layer: `AppUtils`-built app, FastAPI `TestClient`, gRPC stubs over a real channel
- Testcontainers per `@needs-*` tag (databases, queues, Temporal, …), session-scoped, with per-scenario data reset
- Running a subset: `behave --tags=~@needs-kafka` starts only the containers the selected scenarios need

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

Suggest `/scaffold-bdd` when the user wants a new feature stub.
