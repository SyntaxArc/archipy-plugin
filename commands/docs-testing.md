---
name: docs-testing
description: Open ArchiPy BDD testing guidance
---

# /docs-testing

Read `../skills/archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this
command file inside the plugin installation) — and the BDD testing section of
`../skills/archipy-docs/reference.md`.

Cover:

- Behave layout (`features/`, steps, ScenarioContext)
- Ports/mocks vs `@needs-*` integration tags
- Skipping infra with `behave --tags=~@needs-redis --tags=~@needs-postgres` (every `@needs-*` tag present)

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

Suggest `/scaffold-bdd` when the user wants a new feature stub.
