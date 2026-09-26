import logging
import uuid

from archipy.adapters.base.sqlalchemy.session_manager_registry import SessionManagerRegistry
from archipy.configs.base_config import BaseConfig
from behave.model import Scenario
from behave.runner import Context
from pydantic_settings import SettingsConfigDict
from testcontainers.core.config import testcontainers_config

from configs.app_config import AppConfig  # ADAPT: the app's BaseConfig subclass
from features.app_harness import AppHarness
from features.scenario_context_pool_manager import ScenarioContextPoolManager
from features.test_containers import ContainerManager


class TestConfig(AppConfig):
    """App config for tests; container endpoints are patched in when each container starts."""

    model_config = SettingsConfigDict(env_file=".env.test")

    # Images for every container the app may tag (versions ArchiPy tests against); override in .env.test.
    POSTGRES__IMAGE: str = "postgres:18.6-alpine"
    MYSQL__IMAGE: str = "mysql:8.4.11"
    REDIS__IMAGE: str = "redis:8.10.1-alpine"
    KAFKA__IMAGE: str = "apache/kafka:4.3.1"
    TEMPORAL__IMAGE: str = "temporalio/temporal:1.8.2"
    MINIO__IMAGE: str = "pgsty/minio:RELEASE.2026-08-04T00-00-00Z"
    ELASTIC__IMAGE: str = "elastic/elasticsearch:9.5.4"
    KEYCLOAK__IMAGE: str = "keycloak/keycloak:26.7.4"
    VAULT__IMAGE: str = "hashicorp/vault:2.0.4"
    SCYLLADB__IMAGE: str = "scylladb/scylla:2026.2.5"
    TESTCONTAINERS_RYUK_CONTAINER_IMAGE: str | None = None


config = TestConfig()
BaseConfig.set_global(config)
if config.TESTCONTAINERS_RYUK_CONTAINER_IMAGE:
    testcontainers_config.ryuk_image = config.TESTCONTAINERS_RYUK_CONTAINER_IMAGE


def _needed_containers(context: Context) -> set[str]:
    """Union of @needs-* tags across the scenarios this run will execute (honours `behave --tags`)."""
    tag_expression = context.config.tag_expression
    tags: list[str] = []
    for feature in context._runner.features:
        for scenario in feature.walk_scenarios():
            if scenario.should_run_with_tags(tag_expression):
                tags.extend(str(tag) for tag in scenario.effective_tags)
    return ContainerManager.extract_containers_from_tags(tags)


def before_all(context: Context) -> None:
    logging.basicConfig(level=logging.INFO)
    context.logger = logging.getLogger("behave.tests")
    context.scenario_context_pool = ScenarioContextPoolManager()
    # Start every tagged container before the app exists: engines and clients bind to endpoints at construction,
    # and ArchiPy session managers are singletons, so containers live for the whole run.
    ContainerManager.start_containers(_needed_containers(context))
    context.app = AppHarness()
    context.app.start()


def before_scenario(context: Context, scenario: Scenario) -> None:
    missing = ContainerManager.extract_containers_from_tags([str(t) for t in scenario.effective_tags])
    missing -= ContainerManager.running()
    if missing:
        raise RuntimeError(f"Containers {sorted(missing)} were not started in before_all")
    if not hasattr(scenario, "id"):
        scenario.id = str(uuid.uuid4())
    context.scenario_context_pool.get_context(scenario.id)


def after_scenario(context: Context, scenario: Scenario) -> None:
    scenario_id = getattr(scenario, "id", "unknown")
    context.scenario_context_pool.cleanup_context(scenario_id)
    context.app.reset()


def after_all(context: Context) -> None:
    if hasattr(context, "app"):
        context.app.stop()
    if hasattr(context, "scenario_context_pool"):
        context.scenario_context_pool.cleanup_all()
    SessionManagerRegistry.reset()
    ContainerManager.stop_all()
