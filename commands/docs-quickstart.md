---
name: docs-quickstart
description: Open ArchiPy quickstart guidance for app teams
---

# /docs-quickstart

Read `../skills/archipy-docs/SKILL.md` in full — use the **archipy-docs** skill (resolve `../...` relative to this
command file inside the plugin installation) — and the Quickstart section of `../skills/archipy-docs/reference.md`.

Summarize for the user:

1. Python 3.14+ and `uv`
2. `uv add "archipy[<extras>]"`
3. `AppConfig(BaseConfig)` + `set_global`
4. First adapter usage

Live docs: https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/

Offer `/scaffold-app` if they want files generated, or `/scaffold-models` for DTOs and errors.
