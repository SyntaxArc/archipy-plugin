---
name: docs-quickstart
description: Open ArchiPy quickstart guidance for app teams
disable-model-invocation: true
---

# /docs-quickstart

Read `../archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../archipy-docs/`) — and the Quickstart section of `../archipy-docs/reference.md`.

Summarize for the user:

1. Python 3.14+ and `uv`
2. `uv add "archipy[<extras>]"`
3. `AppConfig(BaseConfig)` + `set_global`
4. First adapter usage

Live docs: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

Offer `/scaffold-app` if they want files generated, or `/scaffold-models` for DTOs and errors.
