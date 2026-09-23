---
name: docs-adapters
description: Open ArchiPy adapter patterns and API docs for app teams
disable-model-invocation: true
---

# /docs-adapters

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and the Adapters section of `../archipy-docs/reference.md`.

Cover:

- Prefer ArchiPy extras + shipped adapters
- Domain wrappers under `repositories/{domain}/adapters/` (e.g. `user_db_adapter.py`)
- Boundary error mapping (`raise ... from e`)

Live docs:

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/

Offer `/scaffold-adapter` if they want files generated.
