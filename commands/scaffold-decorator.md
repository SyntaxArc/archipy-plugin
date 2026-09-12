---
name: scaffold-decorator
description: Scaffold or wire a helpers/decorators module (prefer ArchiPy decorators)
---

# /scaffold-decorator

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/scaffold-archipy-decorator/SKILL.md` (canonical workflow — follow it in full)
- `../rules/using-archipy-decorators.mdc` (prefer ArchiPy decorators; UoW on logics)
- `../skills/archipy-docs/reference.md` (Decorators section)

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: existing decorators, call sites, and the installed ArchiPy version for
a matching decorator. Infer sync/async style and project naming from the target call site. Scope is **only**
`helpers/decorators/` — never create utils or interceptors here.

## 2. Ask only for unresolved choices

- Behavior to wrap; sync vs async
- Built-in ArchiPy decorator vs custom (prefer ArchiPy whenever it fits)

Preserve existing decorator modules; do not overwrite.

## 3. Generate

1. Prefer ArchiPy: `ttl_cache_decorator`, `postgres_sqlalchemy_atomic_decorator` (+ async twin),
   `trace_span` / `trace_root` (+ async twins) from `archipy.helpers.decorators.tracing`, `measure_duration` /
   `count_calls` (+ async twins) from `archipy.helpers.decorators.metrics`, `timeout_decorator`,
   `retry_decorator`, `singleton_decorator`, `timing_decorator`, `grpc_rate_limit_decorator`. Show correct usage on
   a sample function; do not reimplement. UoW decorators belong on **logics**, not services/repositories.
2. Custom decorator: create `helpers/decorators/<name>.py` with `functools.wraps`, preserved types
   (`ParamSpec` / `TypeVar`), Google-style docstring with Args/Returns and a usage example. Separate sync/async
   wrappers if both needed.

## 4. Do not

- **No** concrete adapter imports at module level; do not construct adapters inside decorator modules.
- Sync decorators must reject coroutine functions — use async twins instead.
- Do not create utils or interceptors in this step.

## 5. Verify and report

1. Run formatter/linter and focused tests for return values, exceptions, and metadata/signature preservation.
2. Report the reused ArchiPy API or files created, plus commands run.

Reference: `../skills/archipy-docs/reference.md` (Decorators). Docs: https://syntaxarc.github.io/ArchiPy/tutorials/helpers/
