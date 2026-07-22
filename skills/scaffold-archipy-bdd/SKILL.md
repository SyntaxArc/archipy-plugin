---
name: scaffold-archipy-bdd
description: >-
  Scaffold Behave BDD layout for an ArchiPy app (feature, steps, ScenarioContext,
  pool manager, environment, optional testcontainers). Use when adding acceptance
  tests under features/.
---

# Scaffold ArchiPy BDD

## Before writing files

Ask the user for:

1. Feature name / file stem (e.g. `user_registration`)
2. Mode: **mocks only** vs **infra** (`@needs-*` + testcontainers)

## Prefer ArchiPy

```bash
uv add "archipy[behave]"
# infra mode also:
uv add "archipy[testcontainers]"
```

## Generate

Under **project root** (create shared files only if missing):

```text
features/
├── <name>.feature
├── steps/
│   └── <name>_steps.py
├── scenario_context.py              # always — adapt from ArchiPy pattern
├── scenario_context_pool_manager.py # always — Singleton pool
├── environment.py                   # always — behave hooks
├── test_helpers.py                  # always — get_current_scenario_context
└── test_containers.py               # infra mode only — ContainerManager + needed containers
.env.test                            # infra mode — REDIS__IMAGE, POSTGRES__IMAGE, …
```

Model after ArchiPy `features/` + docs tutorial (consumer-slim — no library gRPC/Temporal special cases unless the app needs them).

---

### `features/scenario_context.py`

Per-scenario storage + cleanup (`adapter`, `async_adapter`, `db_file`, `entities`, `store`/`get`):

```python
import asyncio
import logging
import os
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


class ScenarioContext:
    """Per-scenario isolated storage — prevents cross-scenario contamination."""

    def __init__(self, scenario_id: UUID | str) -> None:
        self.scenario_id = scenario_id
        self.storage: dict[str, Any] = {}
        self.db_file: str | None = None
        self.adapter: Any = None
        self.async_adapter: Any = None
        self.entities: dict[str, Any] = {}
        self.entity_ids: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store an object under key."""
        self.storage[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Return stored object or default."""
        return self.storage.get(key, default)

    def cleanup(self) -> None:
        """Close adapters and remove temp DB files."""
        if self.adapter:
            try:
                if hasattr(self.adapter, "close") and not hasattr(self.adapter, "session_manager"):
                    self.adapter.close()
                elif hasattr(self.adapter, "session_manager") and hasattr(self.adapter.session_manager, "engine"):
                    self.adapter.session_manager.remove_session()
                    self.adapter.session_manager.engine.dispose()
            except Exception:
                logger.exception("Error disposing adapter")

        if self.async_adapter:
            try:
                try:
                    asyncio.get_running_loop()
                    asyncio.create_task(self.async_cleanup())
                except RuntimeError:
                    asyncio.run(self.async_cleanup())
            except Exception:
                logger.exception("Error in async cleanup")

        if self.db_file and os.path.exists(self.db_file):
            try:
                os.remove(self.db_file)
            except OSError:
                logger.exception("Error removing database file")

    async def async_cleanup(self) -> None:
        """Dispose async adapter resources."""
        if not self.async_adapter:
            return
        try:
            if hasattr(self.async_adapter, "close") and not hasattr(self.async_adapter, "session_manager"):
                await self.async_adapter.close()
            elif hasattr(self.async_adapter, "session_manager") and hasattr(
                self.async_adapter.session_manager,
                "engine",
            ):
                await self.async_adapter.session_manager.remove_session()
                await self.async_adapter.session_manager.engine.dispose()
        except Exception:
            logger.exception("Error in async adapter cleanup")
```

---

### `features/scenario_context_pool_manager.py`

```python
from uuid import UUID

from archipy.helpers.metaclasses.singleton import Singleton
from features.scenario_context import ScenarioContext


class ScenarioContextPoolManager(metaclass=Singleton):
    """Singleton pool: scenario ID → ScenarioContext."""

    def __init__(self) -> None:
        self.context_pool: dict[UUID | str, ScenarioContext] = {}

    def get_context(self, scenario_id: UUID | str) -> ScenarioContext:
        """Get or create context for scenario_id."""
        if scenario_id not in self.context_pool:
            self.context_pool[scenario_id] = ScenarioContext(scenario_id)
        return self.context_pool[scenario_id]

    def cleanup_context(self, scenario_id: UUID | str) -> None:
        """Cleanup and remove one scenario context."""
        if scenario_id in self.context_pool:
            self.context_pool[scenario_id].cleanup()
            del self.context_pool[scenario_id]

    def cleanup_all(self) -> None:
        """Cleanup every pooled context."""
        for scenario_id in list(self.context_pool):
            self.context_pool[scenario_id].cleanup()
            del self.context_pool[scenario_id]
```

---

### `features/test_helpers.py`

```python
def get_current_scenario_context(context):
    """Return ScenarioContext for the current behave scenario."""
    if not hasattr(context, "scenario_context_pool"):
        raise AttributeError("No scenario context pool available")
    return context.scenario_context_pool.get_context(context.scenario.id)
```

---

### `features/environment.py` (core hooks)

Mirror ArchiPy lifecycle; **omit** library-only gRPC/Temporal server bootstrap unless the app tests those.

```python
import logging
import uuid

from behave.model import Feature, Scenario
from behave.runner import Context
from features.scenario_context_pool_manager import ScenarioContextPoolManager
from pydantic_settings import SettingsConfigDict

from archipy.adapters.base.sqlalchemy.session_manager_registry import SessionManagerRegistry
from archipy.configs.base_config import BaseConfig

# Infra mode: also import ContainerManager from features.test_containers


class TestConfig(BaseConfig):
    """Test config; infra mode reads Docker images from .env.test."""

    model_config = SettingsConfigDict(env_file=".env.test")

    # Infra mode — declare only images you use, e.g.:
    # REDIS__IMAGE: str
    # POSTGRES__IMAGE: str


config = TestConfig()
BaseConfig.set_global(config)


def before_all(context: Context) -> None:
    logging.basicConfig(level=logging.INFO)
    context.logger = logging.getLogger("behave.tests")
    context.scenario_context_pool = ScenarioContextPoolManager()
    # Infra: context.test_containers = ContainerManager


def before_feature(context: Context, feature: Feature) -> None:
    """Infra: start containers from @needs-* feature tags only."""
    # if hasattr(feature, "tags") and feature.tags:
    #     tags = [str(t) for t in feature.tags]
    #     required = ContainerManager.extract_containers_from_tags(tags)
    #     if required:
    #         ContainerManager.start_containers(list(required))


def before_scenario(context: Context, scenario: Scenario) -> None:
    if not hasattr(scenario, "id"):
        scenario.id = str(uuid.uuid4())
    scenario_context = context.scenario_context_pool.get_context(scenario.id)
    if hasattr(context, "test_containers"):
        scenario_context.store("test_containers", context.test_containers)


def after_scenario(context: Context, scenario: Scenario) -> None:
    scenario_id = getattr(scenario, "id", "unknown")
    if hasattr(context, "scenario_context_pool"):
        context.scenario_context_pool.cleanup_context(scenario_id)
    SessionManagerRegistry.reset()


def after_feature(context: Context, feature: Feature) -> None:
    if hasattr(context, "test_containers"):
        context.test_containers.stop_all()


def after_all(context: Context) -> None:
    if hasattr(context, "test_containers"):
        context.test_containers.stop_all()
    if hasattr(context, "scenario_context_pool"):
        context.scenario_context_pool.cleanup_all()
```

Uncomment / wire `ContainerManager` when mode is infra.

---

### `features/test_containers.py` (infra mode)

Copy **pattern** from ArchiPy `features/test_containers.py`, not the full multi-service registry:

1. `TAG_CONTAINER_MAP` (`needs-redis` → `redis`, …)
2. `ContainerManager` with `register`, `get_container`, `start_containers`, `extract_containers_from_tags`, `stop_all`
3. Only register containers the app actually tests (e.g. one `RedisTestContainer` Singleton that starts `RedisContainer`, patches `BaseConfig.global_config().REDIS`)

Do **not** paste ArchiPy’s entire container catalogue or gRPC test servers.

---

### Feature + steps

- Gherkin source of truth; tag infra `@needs-redis` / `@needs-postgres` / …
- Steps: `get_current_scenario_context(context)` or `context.scenario_context_pool.get_context(context.scenario.id)`
- Mocks mode: inject `RedisMock` into scenario context — no Docker
- Skip infra: `uv run behave --tags=~@needs-redis`

## Constraints

- Behave only (not pytest) as primary style.
- No shared mutable globals across scenarios.
- Dispose context after each scenario; `stop_all` after feature/all when using containers.
- Consumer apps: slim templates — library `environment.py` gRPC/Temporal blocks are ArchiPy-core specific.

## Docs

- https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
