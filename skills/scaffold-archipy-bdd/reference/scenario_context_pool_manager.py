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
