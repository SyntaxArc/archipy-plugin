"""Example domain RediSearch full-text adapter — rename Product* to your domain."""

from __future__ import annotations

import logging

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.adapters.redis.search_ports import RedisSearchHandlePort
from archipy.models.dtos.redis.search.index_schema_dto import (
    IndexSchemaDTO,
    NumericFieldConfig,
    TagFieldConfig,
    TextFieldConfig,
)
from archipy.models.dtos.redis.search.search_query_dto import SearchQueryDTO
from archipy.models.dtos.redis.search.search_result_dto import SearchResultDTO
from archipy.models.types.redis_search_types import RedisIndexType

# Define under models/errors/ for the domain — do not leave this import dangling.
from my_app.models.errors.product_errors import ProductSearchError

logger = logging.getLogger(__name__)


class ProductSearchAdapter:
    """Thin RediSearch wrapper for product full-text search via ArchiPy."""

    INDEX_NAME = "idx:product"
    PREFIX = "product:"

    def __init__(self, redis_adapter: RedisAdapter) -> None:
        self._redis = redis_adapter
        self._handle: RedisSearchHandlePort = redis_adapter.search_index(self.INDEX_NAME)

    def ensure_index(self) -> None:
        """Create the RediSearch index if it does not exist."""
        try:
            self._handle.info()
            return
        except Exception as info_exc:
            logger.debug("Index %s missing or unreadable: %s", self.INDEX_NAME, info_exc)

        schema = IndexSchemaDTO(
            fields=[
                TextFieldConfig(name="name"),
                TextFieldConfig(name="description"),
                TagFieldConfig(name="category"),
                NumericFieldConfig(name="price"),
            ],
            index_type=RedisIndexType.HASH,
        )
        try:
            self._handle.create_index(schema, prefix=self.PREFIX)
        except Exception as create_exc:
            raise ProductSearchError("Failed to create product search index") from create_exc

    def upsert_document(self, product_id: str, fields: dict[str, str | float]) -> None:
        """Index or update a product hash document."""
        try:
            self._handle.upsert_hash(f"{self.PREFIX}{product_id}", fields)
        except Exception as exc:
            raise ProductSearchError(f"Failed to upsert product {product_id}") from exc

    def search(self, query_text: str, *, offset: int = 0, limit: int = 20) -> SearchResultDTO:
        """Run a full-text query."""
        try:
            return self._handle.search(
                SearchQueryDTO(query=query_text, offset=offset, limit=limit),
            )
        except Exception as exc:
            raise ProductSearchError("Product search query failed") from exc
