---
name: redis-search
description: Scaffold Redis search adapters (RediSearch full-text, vector, search caching)
---

# /redis-search

## 0. Mandatory reads — do this first, before generating anything

Read these files in full. Resolve `../...` paths relative to this command file inside the plugin installation
(`commands/` and `skills/` are siblings; e.g. `$CURSOR_PLUGIN_ROOT/commands/` or `$CLAUDE_PLUGIN_ROOT/commands/` —
follow symlinks). Do not rely on the summaries below alone.

- `../skills/redis-search/SKILL.md` (canonical workflow — follow it in full)
- `../skills/archipy-docs/reference.md` (Adapters + Redis Search sections — layout and ArchiPy constraints)
- `../rules/using-archipy-adapters.mdc` (ports, sync/async split, boundary errors)

Copy skill templates from `reference/` resolved relative to the skill's `SKILL.md` location in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/redis-search/` or `$CLAUDE_PLUGIN_ROOT/skills/redis-search/`):
`reference/fulltext_adapter.py`, `reference/vector_adapter.py`, `reference/search_cache_adapter.py`. Copy and adapt
them into the app; never edit the plugin copies.

## 1. Inspect the workspace

Inspect the workspace as directed in the skill: the domain, Redis config/adapters, DTOs, index naming, key prefixes,
DI wiring, and tests. Infer data structure, sync/async style, and existing search conventions.

## 2. Ask only for unresolved choices

- Search type: full-text / vector / search-cache
- Domain, query behavior, and (vector) dimension/metric

Preserve existing indexes and adapters. Treat schema or prefix changes as migrations; do not silently replace them.

## 3. Generate

1. Prefer `uv add "archipy[redis]"` and a thin domain wrapper under `repositories/<domain>/adapters/`:
   `repositories/<domain>/adapters/<domain>_search_adapter.py` (or `_vector_` / `_search_cache_`)
   + `<domain>_repository.py` stub if missing.
2. Copy the matching template from `reference/`, rename class/index/prefix to the domain. Full-text: `ensure_index`
   via `info()` → `create_index(IndexSchemaDTO, …)` only when missing; search via
   `handle.search(SearchQueryDTO(...))`. Vector: `VectorFieldConfig` + `SearchQueryDTO.from_knn` / `from_range`,
   adjust DIM/algorithm. Cache: cache-aside with Redis get/setex; repository orchestrates search + cache, logics own
   invalidation.
3. Define a domain error (e.g. `ProductSearchError`) under `models/errors/` — templates import it. Map Redis failures
   with `raise DomainError(...) from e`.
4. Wire via DI in `configs/containers.py`.

Key library symbols: `RedisAdapter.search_index(name)` / `list_search_indexes()`; DTOs `IndexSchemaDTO`,
`TextFieldConfig`, `TagFieldConfig`, `NumericFieldConfig`, `VectorFieldConfig`; queries `SearchQueryDTO`
(`from_knn` / `from_range`); documents `HashDocumentUpsertDTO` / `JsonDocumentUpsertDTO`; `pack_vector` /
`unpack_vector` from `archipy.adapters.redis.search`. Requires **Redis 8+** (query engine); cluster needs
hash-tagged prefixes (e.g. `{products}:`).

## 4. Do not

- Prefer the ArchiPy search-handle API — never raw `client.ft()` for operations the handle covers.
- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Use specific exceptions; always `raise ... from e`.

## 5. Verify and report

1. Run formatter/linter and focused tests for index creation, query mapping, empty results, and mapped failures.
2. For vector search, verify encoded vector dimension and distance metric match the schema.
3. Run live Redis tests only when the project already provides tagged/containerized infrastructure.
4. Report files, schema assumptions, dependency changes, and commands run.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/ · bundled `../skills/archipy-docs/reference.md`
