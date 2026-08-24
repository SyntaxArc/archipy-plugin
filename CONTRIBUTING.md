# Contributing to archipy-plugin

Consumer plugin for apps that depend on PyPI [`archipy`](https://pypi.org/project/archipy/). This repo is **not** for
maintaining the ArchiPy library itself.

For ArchiPy core changes, use the
[ArchiPy CONTRIBUTING](https://github.com/SyntaxArc/ArchiPy/blob/master/CONTRIBUTING.md) guide.

## Local setup

```bash
# Cursor
mkdir -p ~/.cursor/plugins/local
ln -sfn "$(pwd)" ~/.cursor/plugins/local/archipy

# Claude Code
mkdir -p ~/.claude/plugins/local
ln -sfn "$(pwd)" ~/.claude/plugins/local/archipy
```

Reload the editor after edits.

## Catalog sync checklist

Before every PR that touches skills/commands/AGENTS/README:

1. Every `/command` listed in `AGENTS.md` has a matching `commands/<name>.md`.
2. Every `skills/<name>/SKILL.md` frontmatter `name:` matches the folder name.
3. README `### Rules (N)` / `### Skills (N)` / `### Commands (N)` counts match disk; tables list every entry.
4. Atomic UoW decorator name stays `postgres_sqlalchemy_atomic_decorator` (not a fictional `@atomic` API).

Run:

```bash
python3 scripts/check_catalog.py
python3 -m unittest discover -s tests -v
```

## Dual IDE parity

Keep Cursor and Claude manifests in sync:

| File                              | Field                |
|-----------------------------------|----------------------|
| `.cursor-plugin/plugin.json`      | `version`            |
| `.claude-plugin/plugin.json`      | `version`            |
| `.cursor-plugin/marketplace.json` | `plugins[0].version` |
| `.claude-plugin/marketplace.json` | `plugins[0].version` |

All four must share the same SemVer string.

`hooks` paths **must differ**: Cursor `./hooks/hooks.json`, Claude Code `./hooks/claude-hooks.json`.

## Release checklist

1. Update `CHANGELOG.md` (Keep a Changelog).
2. Bump all four JSON versions together.
3. Run `python3 scripts/check_catalog.py` and `python3 -m unittest discover -s tests -v`.
4. Open a focused PR; conventional commits (`feat`, `fix`, `docs`, `chore`, …).

## Hooks

Plugin hooks:

- Cursor: `hooks/hooks.json` (`sessionStart`, `postToolUse`) via `${CURSOR_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}`
- Claude Code: `hooks/claude-hooks.json` (`SessionStart`, `PostToolUse`) via `${CLAUDE_PLUGIN_ROOT}`

Claude Code does not load `.mdc` rules. `scripts/scaffold_hygiene.py SessionStart` / `PostToolUse` injects matching
rule bodies. Do not point both manifests at the same hooks file — schemas differ.

## Scope reminders

- Apps: models data-only; logics UoW + rules; services thin transport.
- Domain adapters under `repositories/{domain}/adapters/` only.
- No graphify / library changelog / ArchiPy monorepo maintainer tooling in this plugin.
