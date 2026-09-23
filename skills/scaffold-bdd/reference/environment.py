import logging
import uuid
from archipy.adapters.base.sqlalchemy.session_manager_registry import SessionManagerRegistry
from archipy.configs.base_config import BaseConfig
from behave.model import Feature, Scenario
from behave.runner import Context
from features.scenario_context_pool_manager import ScenarioContextPoolManager
from pydantic_settings import SettingsConfigDict


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
