---
name: redis-search
description: >-
  Scaffold Redis search adapters for full-text search (RediSearch), vector search,
  and search caching patterns. Use when adding search infrastructure to ArchiPy apps.
  Prefer RedisAdapter.search_index() over raw client.ft().
---

# Redis Search Skills

## Overview

Redis search via ArchiPy (`archipy[redis]`):

- **RediSearch**: full-text via `RedisAdapter.search_index(name)` → `RedisSearchHandle`
- **Vector search**: KNN / range via `SearchQueryDTO.from_knn` / `from_range`
- **Search caching**: cache-aside around expensive search results

Canonical layout and ArchiPy constraints: `../archipy-docs/reference.md` (Adapters + Redis Search).
Templates: `reference/fulltext_adapter.py`, `reference/vector_adapter.py`, `reference/search_cache_adapter.py`.

## Before writing files

Ask the user for:

1. Search type: full-text, vector, or caching
2. Domain name (e.g. `product`, `document`)
3. Data structure to index (HASH vs JSON)
4. Search patterns needed (autocomplete, faceted search, …)
5. Sync or async (or both as separate classes)

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

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Prefer ArchiPy search handle API; only drop to raw Redis for operations the handle does not cover.
- Use specific exceptions; always `raise ... from e`.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/ (Redis Search section)
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
- Bundled: `../archipy-docs/reference.md`
