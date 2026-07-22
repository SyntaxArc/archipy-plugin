---
name: docs-testing
description: Open ArchiPy BDD testing guidance
---

# /docs-testing

Use the **archipy-docs** skill and the BDD testing section of `skills/archipy-docs/reference.md`.

Cover:

- Behave layout (`features/`, steps, ScenarioContext)
- Ports/mocks vs `@needs-*` integration tags
- Skipping infra with `behave --tags=~@needs-*`

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/

Suggest `/scaffold-bdd` when the user wants a new feature stub.
