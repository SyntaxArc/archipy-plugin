"""Example domain Redis vector-search adapter — rename Product* to your domain."""

from __future__ import annotations

import logging

from archipy.adapters.redis.adapters import RedisAdapter
from archipy.adapters.redis.search_ports import RedisSearchHandlePort
from archipy.models.dtos.redis.search.index_schema_dto import (
    IndexSchemaDTO,
    TagFieldConfig,
    VectorFieldConfig,
)
from archipy.models.dtos.redis.search.search_query_dto import SearchQueryDTO
from archipy.models.dtos.redis.search.search_result_dto import SearchResultDTO
from archipy.models.types.redis_search_types import (
    RedisIndexType,
    VectorAlgorithm,
    VectorDistanceMetric,
)

from my_app.models.errors.product_errors import ProductSearchError

logger = logging.getLogger(__name__)


class ProductVectorAdapter:
    """Thin Redis vector-search wrapper for product embeddings via ArchiPy."""

    INDEX_NAME = "idx:product_vec"
    PREFIX = "product_vec:"
    VECTOR_FIELD = "embedding"
    DIM = 1536

    def __init__(self, redis_adapter: RedisAdapter) -> None:
        self._redis = redis_adapter
        self._handle: RedisSearchHandlePort = redis_adapter.search_index(self.INDEX_NAME)

    def ensure_index(self) -> None:
        """Create a HNSW vector index if missing."""
        try:
            self._handle.info()
            return
        except Exception as info_exc:
            logger.debug("Index %s missing or unreadable: %s", self.INDEX_NAME, info_exc)

        schema = IndexSchemaDTO(
            fields=[
                TagFieldConfig(name="category"),
                VectorFieldConfig(
                    name=self.VECTOR_FIELD,
                    dim=self.DIM,
                    distance_metric=VectorDistanceMetric.COSINE,
                    algorithm=VectorAlgorithm.HNSW,
                ),
            ],
            index_type=RedisIndexType.HASH,
        )
        try:
            self._handle.create_index(schema, prefix=self.PREFIX)
        except Exception as create_exc:
            raise ProductSearchError("Failed to create product vector index") from create_exc

    def knn_search(self, query_vector: list[float], *, k: int = 10) -> SearchResultDTO:
        """Return top-k similar documents for an embedding."""
        try:
            return self._handle.search(
                SearchQueryDTO.from_knn(
                    query_vector,
                    k=k,
                    return_fields=["category"],
                ),
            )
        except Exception as exc:
            raise ProductSearchError("Product vector search failed") from exc
