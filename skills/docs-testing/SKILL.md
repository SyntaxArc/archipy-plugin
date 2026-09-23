---
name: docs-testing
description: Open ArchiPy BDD testing guidance
disable-model-invocation: true
---

# /docs-testing

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and the BDD testing section of
`../archipy-docs/reference.md`.

Cover:

- Behave layout (`features/`, steps, ScenarioContext)
- Ports/mocks vs `@needs-*` integration tags
- Skipping infra with `behave --tags=~@needs-redis --tags=~@needs-postgres` (every `@needs-*` tag present)

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

Suggest `/scaffold-bdd` when the user wants a new feature stub.
