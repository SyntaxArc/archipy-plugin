---
name: redis-search
description: >-
  Scaffold Redis search adapters for full-text search (RediSearch), vector search,
  and search caching patterns. Use when adding search infrastructure to ArchiPy apps.
---

# Redis Search Skills

## Overview

Redis provides powerful search capabilities through modules:
- **RediSearch**: Full-text search with advanced querying
- **Redis Vector Search**: Similarity search for embeddings/AI
- **Search Caching**: Patterns for caching search results

## Before writing files

Ask the user for:

1. Search type: full-text, vector, or caching
2. Domain name (e.g. `product`, `document`)
3. Data structure to index (hash, JSON, etc.)
4. Search patterns needed (autocomplete, faceted search, etc.)
5. Sync or async (or both as separate classes)

## Prefer ArchiPy

If ArchiPy already ships the client, prefer:

```bash
uv add "archipy[redis]"
```

and a thin domain wrapper — not a full reimplementation.

## Generate

### Full-text search (RediSearch)

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_search_adapter.py   # RediSearch wrapper
└── <domain>_repository.py           # create stub if missing
```

### Vector search

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_vector_adapter.py   # Vector search wrapper
└── <domain>_repository.py           # create stub if missing
```

### Search caching

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_search_cache_adapter.py  # Cache-aside pattern
└── <domain>_repository.py                # create stub if missing
```

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Wire via DI in `configs/containers.py`.
- Use specific exceptions; always `raise ... from e`.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/