# ArchiPy Reference: Adapters, entities, and unit of work

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## Adapters (sketch)

```python
from archipy.adapters.redis.adapters import RedisAdapter

redis = RedisAdapter()  # uses global config.REDIS
```

Domain wrappers live under `repositories/{domain}/adapters/` (e.g. `user_db_adapter.py`, `user_cache_adapter.py`).
Prefer thin wrappers around ArchiPy adapters. Map **specific** client errors to domain errors with `raise ... from e`.
Keep sync/async as separate classes. Inject ports into logics/repos.

### Adapter families (library)

Use ArchiPy before inventing clients — extras as above:

| Family                                   | Notes                                                           |
|------------------------------------------|-----------------------------------------------------------------|
| Redis (+ RediSearch)                     | `RedisAdapter.search_index(name)` → handle; see `/redis-search` |
| Postgres / SQLite / StarRocks SQLAlchemy | sync + async adapters; pair with atomic decorators              |
| Kafka, ScyllaDB, MinIO, Keycloak         | dedicated adapters                                              |
| Elasticsearch (+ async)                  | search / document APIs                                          |
| Email                                    | email adapter                                                   |
| Temporal                                 | adapter + `worker.py` / `runtime.py`                            |
| Parsian / Saman IPG                      | Iranian payment gateways                                        |

### Redis Search (library API)

```python
from archipy.adapters.redis.adapters import RedisAdapter
from archipy.models.dtos.redis.search.index_schema_dto import (
    IndexSchemaDTO,
    TagFieldConfig,
    TextFieldConfig,
)
from archipy.models.dtos.redis.search.search_query_dto import SearchQueryDTO
from archipy.models.types.redis_search_types import RedisIndexType

redis = RedisAdapter()
handle = redis.search_index("products")
# redis.list_search_indexes()

schema = IndexSchemaDTO(
    fields=[
        TextFieldConfig(name="title"),
        TagFieldConfig(name="category"),
    ],
    index_type=RedisIndexType.HASH,
)
handle.create_index(schema, prefix="product:")
handle.upsert_hash("product:1", {"title": "Redis Guide", "category": "books"})
result = handle.search(SearchQueryDTO(query="@title:Redis", offset=0, limit=20))
```

Do **not** call raw `client.ft()` in app adapters when the handle API covers the case. DTOs live under
`archipy.models.dtos.redis.search.*`; types under `archipy.models.types.redis_search_types`.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/adapters/

## Entities (SQLAlchemy)

Prefer ArchiPy base entities:

```python
from archipy.models.entities.sqlalchemy.base_entities import BaseEntity
```

App entities subclass library bases (`UpdatableEntity`, `DeletableEntity`, …); keep I/O out of `models/`.

## SessionManagerRegistry + atomic family

Atomic decorators resolve the active SQLAlchemy session through
`archipy.adapters.base.sqlalchemy.session_manager_registry.SessionManagerRegistry`. Register the app's session manager
at bootstrap; BDD hooks call `SessionManagerRegistry.reset()` after each scenario.

| Decorator                                                     | Extra / stack                   |
|---------------------------------------------------------------|---------------------------------|
| `postgres_sqlalchemy_atomic_decorator`                        | `postgres` + `sqlalchemy`       |
| `async_postgres_sqlalchemy_atomic_decorator`                  | `postgres` + `sqlalchemy-async` |
| `sqlite_sqlalchemy_atomic_decorator` / `async_sqlite_…`       | SQLite stacks                   |
| `starrocks_sqlalchemy_atomic_decorator` / `async_starrocks_…` | StarRocks stacks                |
| `sqlalchemy_atomic_decorator`                                 | Generic SQLAlchemy              |

Import from `archipy.helpers.decorators.sqlalchemy_atomic` (lazy-loaded via
`archipy.helpers.decorators` `__getattr__` so SQLAlchemy is not a hard import).

## Logics (unit of work)

- Domain DTO in → domain DTO out; no FastAPI/gRPC imports.
- Public methods: decorate with the matching `*_sqlalchemy_atomic_decorator` when using SQLAlchemy.
- May call other domain logics (nested atomic reuses the open session); **never** another domain's repository.
