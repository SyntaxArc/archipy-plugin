---
name: docs-helpers
description: Open ArchiPy helpers docs (utils, decorators, interceptors)
disable-model-invocation: true
---

# /docs-helpers

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and `../archipy-docs/reference/helpers.md`.

Explain the three packages separately:

| Package                | Role                            | Scaffold command        |
|------------------------|---------------------------------|-------------------------|
| `helpers/utils`        | Pure utilities                  | `/scaffold-utils`       |
| `helpers/decorators`   | Cross-cutting function wrappers | `/scaffold-decorator`   |
| `helpers/interceptors` | Request/RPC hooks               | `/scaffold-interceptor` |

Live docs: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
