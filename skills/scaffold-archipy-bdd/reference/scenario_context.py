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
