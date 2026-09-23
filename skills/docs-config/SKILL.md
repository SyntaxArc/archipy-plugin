---
name: docs-config
description: Open ArchiPy configuration and dependency-injection guidance
disable-model-invocation: true
---

# /docs-config

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and the BaseConfig / Dependency injection sections of
`../archipy-docs/reference.md`.

Cover:

- Extending `BaseConfig` and `customize()`
- `set_global` / `global_config`
- `.env.example` (no secrets in git)
- DI container wiring with `archipy[dependency-injection]`

Live docs:

- https://syntaxarc.github.io/ArchiPy/tutorials/config_management/
- https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/
