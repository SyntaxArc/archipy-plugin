---
name: scaffold-interceptor
description: Scaffold or wire a helpers/interceptors module (prefer ArchiPy interceptors)
---

# /scaffold-interceptor

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-interceptor/SKILL.md` (canonical workflow — follow it in full)
- `../rules/using-archipy-interceptors.mdc` (cross-cutting hooks; prefer AppUtils auto-register)
- `../skills/archipy-docs/reference.md` (Interceptors section)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: app bootstrap, existing interceptors/middleware, DI wiring, and the
installed ArchiPy version. Infer framework and sync/async style from the repository. Scope is **only**
`helpers/interceptors/` — never create utils or decorators here.

## 2. Ask only for unresolved choices

- Cross-cutting concern; framework (FastAPI / gRPC); sync vs async
- Built-in ArchiPy interceptor vs custom (prefer ArchiPy + AppUtils auto-registration whenever it fits)

Preserve existing registration order and modules; do not overwrite.

## 3. Generate

1. Check `archipy.helpers.interceptors` (FastAPI / gRPC) first; show registration via DI or framework APIs and stop
   when a stock interceptor fits.
2. Custom interceptor: create under `helpers/interceptors/` (cross-cutting only, e.g. request-ID middleware). Wire
   through `configs/containers.py`, `AppUtils`, or framework middleware registration. Map errors at the boundary;
   do not leak raw exceptions.

## 4. Do not

- Keep cross-cutting only — no domain use-case logic, no domain business writes.
- No adapter construction inside the interceptor module; do not register by importing interceptors from adapters.
- Do not create utils or decorators in this step.

## 5. Verify and report

1. Run formatter/linter and focused transport tests for ordering, success, and mapped failure behavior. Confirm
   registration occurs once.
2. Report the reused ArchiPy API or files created, plus commands run.

Reference: `../skills/archipy-docs/reference.md` (Interceptors). Docs: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
