---
name: scaffold-utils
description: Scaffold or wire a helpers/utils module (prefer ArchiPy utils)
---

# /scaffold-utils

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-utils/SKILL.md` (canonical workflow — follow it in full)
- `../rules/using-archipy-utils.mdc` (pure utilities, AppUtils factories)
- `../skills/archipy-docs/reference.md` (Utils section — check ArchiPy ships it first)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: existing helpers and the installed ArchiPy version for a matching
utility. Infer project naming and function/class style. Scope is **only** `helpers/utils/` — never create decorators
or interceptors here.

## 2. Ask only for unresolved choices

- Purpose / behavior of the util
- Built-in ArchiPy util vs custom (prefer ArchiPy whenever it fits)

Preserve existing helper modules; do not overwrite.

## 3. Generate

1. If ArchiPy provides it, show import + usage only — do not duplicate.
2. Otherwise scaffold a pure util under `helpers/utils/<name>_utils.py` (Google-style docstrings, full type hints,
   double quotes) and show a brief usage snippet in the reply.

## 4. Do not

- Pure functions/classes — no I/O, no DB, no adapters. Never open DB/Redis clients in utils.
- No adapter construction at module level; lazy-import optional deps inside functions when needed.
- Do not create decorators or interceptors in this step (use `/scaffold-decorator`, `/scaffold-interceptor`).

## 5. Verify and report

1. Run the repository's formatter, linter, and focused unit tests.
2. Report the reused ArchiPy API or files created, plus commands run.

Reference: `../skills/archipy-docs/reference.md` (Utils). Docs: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
