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

Before every PR that touches skills/agents/AGENTS/README:

1. Every `/name` listed in `AGENTS.md` has a matching `skills/<name>/SKILL.md` (skills are slash commands).
2. Every `skills/<name>/SKILL.md` frontmatter `name:` matches the folder name.
3. `docs-*` skills set `disable-model-invocation: true` (user shortcuts into `archipy-docs`); all other skills stay
   model-invocable. Scaffold skills need `## Before writing files`, `## Do not`, and `## Verify` ending in a report.
4. README `### Rules (N)` / `### Skills (N)` / `### Commands (N)` counts match disk; tables list every entry.
5. Atomic UoW decorator name stays `postgres_sqlalchemy_atomic_decorator` (not a fictional `@atomic` API).

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
4. Open a focused PR; conventional commits (`feat`, `fix`, `docs`, `chore`, …). Merge after CI is green.
5. Tag the merge commit `vX.Y.Z` and push the tag. `.github/workflows/release.yml` re-runs the checks, verifies the
   tag matches the manifest version, and publishes the GitHub release from the CHANGELOG section. Do not create the
   release by hand.

## Hooks

Plugin hooks (both run `scripts/scaffold_hygiene.py`; keep Cursor and Claude Code behavior in parity):

| Event | Cursor (`hooks/hooks.json`) | Claude Code (`hooks/claude-hooks.json`) |
|---|---|---|
| Session start | `sessionStart` → `additional_context`: reminder + ArchiPy version | `SessionStart` → `hookSpecificOutput.additionalContext`: reminder + version + always-on rule bodies |
| Before Write | `preToolUse` → `permission: "deny"` for a **new** file under a top-level `adapters/` | `PreToolUse` → `permissionDecision: "deny"`, same condition |
| After edits | `postToolUse` → adapter-path warning | `PostToolUse` → warning + glob-matched rule bodies |

- All hooks run only when the project's `pyproject.toml`, `uv.lock`, or `requirements.txt` depends on `archipy`
  (Claude sends `cwd`; Cursor sends `cwd` on tool events and `workspace_roots` everywhere).
- Cursor loads `.mdc` rules natively, so only Claude gets rule bodies. Claude ignores Cursor's top-level
  `additional_context`, and Cursor ignores `hookSpecificOutput`.
- Claude path-scoped rules inject once per session (and subagent), reset on each `SessionStart`
  (startup/resume/clear/compact).
- The adapter guard only blocks creating new files; existing top-level `adapters/` files in legacy apps stay editable.
- Do not point both manifests at the same hooks file — schemas differ.

## Evals

`evals/` holds a `claude plugin eval` suite; see `evals/README.md` for the run command. Run it after changing skill
descriptions or hooks, and compare the with/without-plugin uplift (Δ) against the previous run.

## Scope reminders

- Apps: models data-only; logics UoW + rules; services thin transport.
- Domain adapters under `repositories/{domain}/adapters/` only.
- No library changelog / ArchiPy monorepo maintainer tooling in this plugin.
