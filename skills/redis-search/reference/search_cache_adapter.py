"""Example search-cache adapter — rename Product* to your domain."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any

from archipy.adapters.redis.adapters import RedisAdapter

from my_app.models.errors.product_errors import ProductSearchError


class ProductSearchCacheAdapter:
    """Cache-aside helper for expensive product search results."""

    KEY_PREFIX = "search:product:"
    TTL_SECONDS = 60

    def __init__(self, redis_adapter: RedisAdapter) -> None:
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
            cached = self._redis.get(key)
            if cached is not None:
                if isinstance(cached, bytes):
                    cached = cached.decode()
                return json.loads(cached)
            value = producer()
            self._redis.set(key, json.dumps(value), ex=self.TTL_SECONDS)
            return value
        except ProductSearchError:
            raise
        except Exception as exc:
            raise ProductSearchError("Product search cache failed") from exc
