---
name: redis-search
description: >-
  Scaffold Redis search adapters for full-text search (RediSearch), vector search,
  and search caching patterns. Use when adding search infrastructure to ArchiPy apps.
---

# Redis Search Skills

## Overview

Redis search capabilities via modules:

- **RediSearch**: Full-text search with advanced querying
- **Redis Vector Search**: Similarity search for embeddings/AI
- **Search Caching**: Cache-aside for expensive search results

Canonical layout and ArchiPy constraints: `../archipy-docs/reference.md` (Adapters + Project layout).

## Before writing files

Ask the user for:

1. Search type: full-text, vector, or caching
2. Domain name (e.g. `product`, `document`)
3. Data structure to index (hash, JSON, …)
4. Search patterns needed (autocomplete, faceted search, …)
5. Sync or async (or both as separate classes)

## Prefer ArchiPy

```bash
uv add "archipy[redis]"
```

Thin domain wrapper around ArchiPy Redis adapter — not a full reimplementation.

## Generate

### Full-text search (RediSearch)

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_search_adapter.py
└── <domain>_repository.py
```

Stub shape (`product_search_adapter.py` example — rename to domain):

```python
from __future__ import annotations

import logging
from typing import Any

from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

logger = logging.getLogger(__name__)


class ProductSearchAdapter:
    """Thin RediSearch wrapper for product full-text search."""

    INDEX_NAME = "idx:product"
    PREFIX = "product:"

    def __init__(self, redis_adapter: Any) -> None:
        self._redis = redis_adapter

    def ensure_index(self) -> None:
        """Create the RediSearch index if it does not exist."""
        try:
            self._redis.client.ft(self.INDEX_NAME).info()
        except Exception as exc:
            try:
                self._redis.client.ft(self.INDEX_NAME).create_index(
                    (
                        TextField("name", weight=5.0),
                        TextField("description"),
                        TagField("category"),
                        NumericField("price"),
                    ),
                    definition=IndexDefinition(prefix=[self.PREFIX], index_type=IndexType.HASH),
                )
            except Exception as create_exc:
                raise ProductSearchError("Failed to create product search index") from create_exc
            raise ProductSearchError("Failed to inspect product search index") from exc

    def upsert_document(self, product_id: str, fields: dict[str, str | float]) -> None:
        """Index or update a product hash document."""
        key = f"{self.PREFIX}{product_id}"
        try:
            self._redis.client.hset(key, mapping=fields)
        except Exception as exc:
            raise ProductSearchError(f"Failed to upsert product {product_id}") from exc

    def search(self, query_text: str, *, offset: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """Run a full-text query and return raw document fields."""
        query = Query(query_text).paging(offset, limit)
        try:
            result = self._redis.client.ft(self.INDEX_NAME).search(query)
        except Exception as exc:
            raise ProductSearchError("Product search query failed") from exc
        return [doc.__dict__ for doc in result.docs]
```

Map Redis/RediSearch errors to a domain error (e.g. `ProductSearchError`) with `raise ... from e`.

### Vector search

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_vector_adapter.py
└── <domain>_repository.py
```

Stub shape:

```python
from __future__ import annotations

from typing import Any

from redis.commands.search.field import TagField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query


class ProductVectorAdapter:
    """Thin Redis vector-search wrapper for product embeddings."""

    INDEX_NAME = "idx:product_vec"
    PREFIX = "product_vec:"
    VECTOR_FIELD = "embedding"
    DIM = 1536

    def __init__(self, redis_adapter: Any) -> None:
        self._redis = redis_adapter

    def ensure_index(self) -> None:
        """Create a HNSW vector index if missing."""
        try:
            self._redis.client.ft(self.INDEX_NAME).info()
        except Exception as exc:
            try:
                self._redis.client.ft(self.INDEX_NAME).create_index(
                    (
                        TagField("category"),
                        VectorField(
                            self.VECTOR_FIELD,
                            "HNSW",
                            {
                                "TYPE": "FLOAT32",
                                "DIM": self.DIM,
                                "DISTANCE_METRIC": "COSINE",
                            },
                        ),
                    ),
                    definition=IndexDefinition(prefix=[self.PREFIX], index_type=IndexType.HASH),
                )
            except Exception as create_exc:
                raise ProductSearchError("Failed to create product vector index") from create_exc
            raise ProductSearchError("Failed to inspect product vector index") from exc

    def knn_search(self, query_vector: bytes, *, k: int = 10) -> list[Any]:
        """Return top-k similar documents for a FLOAT32 embedding blob."""
        q = (
            Query(f"*=>[KNN {k} @{self.VECTOR_FIELD} $vec AS score]")
            .sort_by("score")
            .paging(0, k)
            .dialect(2)
        )
        try:
            return self._redis.client.ft(self.INDEX_NAME).search(q, query_params={"vec": query_vector}).docs
        except Exception as exc:
            raise ProductSearchError("Product vector search failed") from exc
```

Adjust `DIM`, field names, and index type (HASH vs JSON) to the domain.

### Search caching

```text
repositories/<domain>/
├── adapters/
│   └── <domain>_search_cache_adapter.py
└── <domain>_repository.py
```

Cache-aside stub:

```python
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable


class ProductSearchCacheAdapter:
    """Cache-aside helper for expensive product search results."""

    KEY_PREFIX = "search:product:"
    TTL_SECONDS = 60

    def __init__(self, redis_adapter: Any) -> None:
        self._redis = redis_adapter

    def _cache_key(self, query: str, filters: dict[str, Any]) -> str:
        raw = json.dumps({"q": query, "f": filters}, sort_keys=True, default=str)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return f"{self.KEY_PREFIX}{digest}"

    def get_or_set(
        self,
        query: str,
        filters: dict[str, Any],
        producer: Callable[[], list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Return cached search hits or compute, store, and return them."""
        key = self._cache_key(query, filters)
        try:
            cached = self._redis.client.get(key)
            if cached is not None:
                return json.loads(cached)
            value = producer()
            self._redis.client.setex(key, self.TTL_SECONDS, json.dumps(value))
            return value
        except Exception as exc:
            raise ProductSearchError("Product search cache failed") from exc
```

Repository orchestrates search adapter + cache; logics own cache invalidation rules.

## Constraints

- Sync and async must be separate classes.
- No business logic in adapters — map data and talk to infrastructure only.
- Do **not** create a top-level `adapters/<name>/` package — domain adapters live under repositories.
- Wire via DI in `configs/containers.py`.
- Use specific exceptions; always `raise ... from e`.
- Prefer ArchiPy Redis client/config from `archipy[redis]`; only add raw `redis` imports for RediSearch/vector APIs the thin wrapper needs.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/adapters/
- https://syntaxarc.github.io/ArchiPy/api_reference/adapters/
- Bundled: `../archipy-docs/reference.md`
