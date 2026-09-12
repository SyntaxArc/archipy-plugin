---
name: scaffold-models
description: Scaffold ArchiPy models (domain/repository DTOs, errors, optional entities)
---

# /scaffold-models

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-models/SKILL.md` (canonical workflow — follow it in full)
- `../rules/using-archipy-models.mdc` (DTO naming, frozen `BaseDTO`, error hierarchy)
- `../rules/architecture-for-apps.mdc` (models are data only; import direction)
- `../skills/archipy-docs/reference.md` (DTO naming)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: existing `models/` DTOs, errors, entities, types, neighboring domains,
and the installed ArchiPy version. Infer domain name and naming from existing modules.

## 2. Ask only for unresolved choices

- Domain / operation names
- Whether entities or types are needed (default: DTOs + errors only)

Preserve existing model modules; do not overwrite.

## 3. Generate

1. Domain DTOs under `models/dtos/<domain>/domain/v{n}/`: `*InputDTO` / `*OutputDTO` extending ArchiPy `BaseDTO`.
2. Repository DTOs under `models/dtos/<domain>/repository/` (never versioned): `*CommandDTO` / `*QueryDTO` /
   `*ResponseDTO`.
3. Domain errors under `models/errors/` subclassing the ArchiPy `BaseError` hierarchy. Export public errors from
   `models/errors/__init__.py` when other layers consume them.
4. Optional `models/entities/` and `models/types/` only when the domain needs them.
5. Verify imports against the app's installed ArchiPy version. Prefer ArchiPy pagination / sort / search DTOs before
   inventing page or cursor shapes.

## 4. Do not

- No I/O, business rules, adapters, DB sessions, or HTTP/gRPC types in models.
- Never import repositories, logics, or services from models.
- Do not version repository DTOs.
- Do not mutate frozen `BaseDTO` instances after validation.

## 5. Verify and report

1. Run the repository's formatter and linter on generated Python.
2. Confirm DTO naming, versioned domain vs unversioned repository layout, and error subclassing.
3. Import the new modules without constructing infrastructure.
4. Report files and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
