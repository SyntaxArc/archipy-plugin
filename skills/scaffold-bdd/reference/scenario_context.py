import logging
from collections.abc import Callable
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


class ScenarioContext:
    """Per-scenario storage (requests, responses, created IDs) — prevents cross-scenario contamination.

    Steps talk to the app only through the harness clients; they never hold adapters or sessions here.
    """

    def __init__(self, scenario_id: UUID | str) -> None:
        self.scenario_id = scenario_id
        self.storage: dict[str, Any] = {}
        self._cleanups: list[Callable[[], None]] = []

    def store(self, key: str, value: Any) -> None:
        """Store an object under key."""
        self.storage[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Return stored object or default."""
        return self.storage.get(key, default)

    def add_cleanup(self, callback: Callable[[], None]) -> None:
        """Run callback when the scenario ends (e.g. close a per-scenario channel)."""
        self._cleanups.append(callback)

    def cleanup(self) -> None:
        """Run cleanups in reverse order and drop stored state."""
        for callback in reversed(self._cleanups):
            try:
                callback()
            except Exception:
                logger.exception("Error in scenario cleanup")
        self._cleanups.clear()
        self.storage.clear()
