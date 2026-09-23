---
name: redis-search
description: >-
  Scaffold RediSearch full-text, vector, or search-cache adapters in an ArchiPy app. Use
  for "add search", "full-text/semantic/vector search", "embeddings index", or "cache
  search results".
---

# Redis Search Skills

## Overview

Redis search via ArchiPy (`archipy[redis]`):

- **RediSearch**: full-text via `RedisAdapter.search_index(name)` → `RedisSearchHandle`
- **Vector search**: KNN / range via `SearchQueryDTO.from_knn` / `from_range`
- **Search caching**: cache-aside around expensive search results

Canonical layout and ArchiPy constraints: `../archipy-docs/reference/adapters.md` (Adapters + Redis Search), resolved relative
to this `SKILL.md`'s directory in the plugin installation — not the app workspace. Templates:
`reference/fulltext_adapter.py`, `reference/vector_adapter.py`, `reference/search_cache_adapter.py`.

Resolve files under `reference/` relative to this `SKILL.md` in the plugin installation
(`$CURSOR_PLUGIN_ROOT/skills/redis-search/` or `${CLAUDE_SKILL_DIR}/`). These are plugin templates,
not app-relative paths. Copy and adapt them into the app; never edit the plugin copies.

## Read first

Read these plugin rules in full before generating files (paths relative to this skill directory; Claude Code: `${CLAUDE_SKILL_DIR}/../../rules/`):

- `../../rules/using-archipy-adapters.mdc`

## Before writing files

1. Inspect the domain, Redis config/adapters, DTOs, index naming, key prefixes, DI wiring, and tests.
2. Infer data structure, sync/async style, and existing search conventions.
3. Ask only for unresolved choices: search type, domain, query behavior, and vector dimension/metric when applicable.
4. Preserve existing indexes and adapters. Treat schema or prefix changes as migrations; do not silently replace them.

## Prefer ArchiPy

```bash
uv add "archipy[redis]"
```

Thin domain wrapper around `RedisAdapter.search_index()` — **not** raw `client.ft()`.

Key library symbols:

- `RedisAdapter.search_index(name)` / `list_search_indexes()`
- DTOs: `IndexSchemaDTO`, `TextFieldConfig`, `TagFieldConfig`, `NumericFieldConfig`, `VectorFieldConfig`
- Queries: `SearchQueryDTO`, `SearchQueryDTO.from_knn(...)`, `SearchQueryDTO.from_range(...)`
- Documents: `HashDocumentUpsertDTO`, `JsonDocumentUpsertDTO`
- Types: `RedisIndexType`, `VectorAlgorithm`, `VectorDistanceMetric`, …
- Helpers: `pack_vector` / `unpack_vector` from `archipy.adapters.redis.search`

Requires **Redis 8+** (query engine). Cluster needs hash-tagged prefixes (e.g. `{products}:`).

## Generate

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_search_adapter.py      # or _vector_ / _search_cache_
└── <domain>_repository.py
```

1. Copy the matching template from `reference/`, rename class/index/prefix to the domain.
2. Define a domain error (e.g. `ProductSearchError`) under `models/errors/` — templates import it.
3. Wire via DI in `configs/containers.py`.
4. Map Redis/RediSearch failures with `raise DomainError(...) from e`.

### Full-text

Use `reference/fulltext_adapter.py`: `ensure_index` via `info()` → `create_index(IndexSchemaDTO, …)` only when missing;
search via `handle.search(SearchQueryDTO(...))`.

### Vector

Use `reference/vector_adapter.py`: `VectorFieldConfig` + `SearchQueryDTO.from_knn`. Adjust `DIM` / algorithm.

### Search caching

Use `reference/search_cache_adapter.py`: cache-aside with Redis get/setex. Repository orchestrates search + cache;
logics own invalidation rules.

## Do not

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Prefer ArchiPy search handle API; only drop to raw Redis for operations the handle does not cover.
- Use specific exceptions; always `raise ... from e`.
- Prefer the ArchiPy search-handle API — never raw `client.ft()` for operations the handle covers.

## Verify

1. Run formatter/linter and focused tests for index creation, query mapping, empty results, and mapped failures.
2. For vector search, verify encoded vector dimension and distance metric match the schema.
3. Run live Redis tests only when the project already provides tagged/containerized infrastructure.
4. Report files, schema assumptions, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/ (Redis Search section)
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
- Bundled: `../archipy-docs/reference.md`
