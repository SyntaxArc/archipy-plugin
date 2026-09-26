"""Testcontainers for BDD: one container per `@needs-*` tag, patched into the global config.

Containers start once per test run (session scope) and stop in `after_all`. ArchiPy session managers and adapters
are singletons that bind to the endpoint they first see, so a container must never be replaced mid-run.

Each container imports its testcontainers module lazily, so apps only need the client libraries for the tags they
actually use. Add a container by subclassing `TestContainer`, registering it, and adding its tag to
`TAG_CONTAINER_MAP`. StarRocks and Redis Cluster are not included; copy them from ArchiPy's
`features/test_containers.py` (https://github.com/SyntaxArc/ArchiPy) if the app needs them.
"""

import logging
from typing import Any, ClassVar

from archipy.configs.base_config import BaseConfig

logger = logging.getLogger(__name__)

TAG_CONTAINER_MAP: dict[str, str] = {
    "needs-postgres": "postgres",
    "needs-mysql": "mysql",
    "needs-redis": "redis",
    "needs-kafka": "kafka",
    "needs-temporal": "temporal",
    "needs-minio": "minio",
    "needs-elasticsearch": "elasticsearch",
    "needs-keycloak": "keycloak",
    "needs-vault": "vault",
    "needs-scylladb": "scylladb",
}

# Hard limits only stop a runaway container; the process settings below keep real usage low.
MEM_LIMITS: dict[str, str] = {
    "postgres": "256m",
    "mysql": "512m",
    "redis": "64m",
    "kafka": "1024m",
    "temporal": "384m",
    "minio": "256m",
    "elasticsearch": "1024m",
    "keycloak": "768m",
    "vault": "128m",
    "scylladb": "1024m",
}


class TestContainer:
    """Base container: build, start once, patch the global config, stop."""

    name: ClassVar[str]

    def __init__(self) -> None:
        self.config = BaseConfig.global_config()
        self.container: Any = None

    @property
    def image(self) -> str:
        """Image from `<NAME>__IMAGE` in TestConfig / .env.test."""
        return getattr(self.config, f"{self.name.upper().replace('-', '_')}__IMAGE")

    def build(self) -> Any:
        """Return an unstarted testcontainers container."""
        raise NotImplementedError

    def wait_ready(self) -> None:
        """Block until the service accepts connections (override when the image needs a log wait)."""

    def configure(self) -> None:
        """Point the global config at the started container."""
        raise NotImplementedError

    def wait_for_log(self, line: str, timeout: int) -> None:
        from testcontainers.core.waiting_utils import wait_for_logs

        wait_for_logs(self.container, line, timeout=timeout)

    def start(self) -> None:
        if self.container is not None:
            return
        self.container = self.build().with_kwargs(mem_limit=MEM_LIMITS[self.name])
        self.container.start()
        self.wait_ready()
        self.configure()
        logger.info("%s container started", self.name)

    def stop(self) -> None:
        if self.container is None:
            return
        self.container.stop()
        self.container = None
        logger.info("%s container stopped", self.name)

    def host(self) -> str:
        return self.container.get_container_host_ip()

    def port(self, internal: int) -> int:
        return int(self.container.get_exposed_port(internal))


class ContainerManager:
    """Registry of test containers keyed by name; starts each one at most once per run."""

    _registry: ClassVar[dict[str, type[TestContainer]]] = {}
    _running: ClassVar[dict[str, TestContainer]] = {}

    @classmethod
    def register(cls, container_class: type[TestContainer]) -> type[TestContainer]:
        cls._registry[container_class.name] = container_class
        return container_class

    @classmethod
    def extract_containers_from_tags(cls, tags: list[str]) -> set[str]:
        names: set[str] = set()
        for tag in tags:
            tag_name = tag.lstrip("@")
            if tag_name in TAG_CONTAINER_MAP:
                names.add(TAG_CONTAINER_MAP[tag_name])
            elif tag_name.startswith("needs-"):
                raise KeyError(f"Unknown container tag @{tag_name}; add it to TAG_CONTAINER_MAP")
        return names

    @classmethod
    def start_containers(cls, names: set[str] | list[str]) -> None:
        for name in sorted(names):
            if name in cls._running:
                continue
            instance = cls._registry[name]()
            instance.start()
            cls._running[name] = instance

    @classmethod
    def get_container(cls, name: str) -> TestContainer:
        return cls._running[name]

    @classmethod
    def running(cls) -> set[str]:
        return set(cls._running)

    @classmethod
    def stop_all(cls) -> None:
        for name in list(cls._running):
            try:
                cls._running.pop(name).stop()
            except Exception:
                logger.exception("Error stopping %s container", name)


@ContainerManager.register
class PostgresTestContainer(TestContainer):
    name = "postgres"

    def build(self) -> Any:
        from testcontainers.postgres import PostgresContainer

        pg = self.config.POSTGRES_SQLALCHEMY
        return PostgresContainer(
            image=self.image,
            dbname=pg.DATABASE or "test_db",
            username=pg.USERNAME or "test_user",
            password=pg.PASSWORD or "test_password",
        ).with_command("postgres -c fsync=off -c synchronous_commit=off -c full_page_writes=off")

    def configure(self) -> None:
        pg = self.config.POSTGRES_SQLALCHEMY
        pg.HOST, pg.PORT = self.host(), self.port(5432)
        pg.DATABASE = self.container.dbname
        pg.USERNAME = self.container.username
        pg.PASSWORD = self.container.password


@ContainerManager.register
class MySQLTestContainer(TestContainer):
    name = "mysql"

    def build(self) -> Any:
        from testcontainers.mysql import MySqlContainer

        mysql = self.config.MYSQL_SQLALCHEMY
        return MySqlContainer(
            image=self.image,
            dbname=mysql.DATABASE or "test_db",
            username=mysql.USERNAME or "test_user",
            password=mysql.PASSWORD or "test_password",
        )

    def configure(self) -> None:
        mysql = self.config.MYSQL_SQLALCHEMY
        mysql.HOST, mysql.PORT = self.host(), self.port(3306)
        mysql.DATABASE = self.container.dbname
        mysql.USERNAME = self.container.username
        mysql.PASSWORD = self.container.password


@ContainerManager.register
class RedisTestContainer(TestContainer):
    name = "redis"

    def build(self) -> Any:
        from testcontainers.redis import RedisContainer

        return RedisContainer(self.image).with_command("redis-server --save '' --appendonly no")

    def configure(self) -> None:
        redis = self.config.REDIS
        redis.MASTER_HOST, redis.PORT, redis.PASSWORD = self.host(), self.port(6379), None


@ContainerManager.register
class KafkaTestContainer(TestContainer):
    """Single-node KRaft broker; the advertised listener must match the host port, so bind it explicitly."""

    name = "kafka"

    def build(self) -> Any:
        import socket

        from testcontainers.core.container import DockerContainer

        with socket.socket() as sock:
            sock.bind(("", 0))
            self._host_port = sock.getsockname()[1]
        env = {
            "KAFKA_NODE_ID": "1",
            "KAFKA_PROCESS_ROLES": "broker,controller",
            "KAFKA_LISTENERS": "PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093",
            "KAFKA_ADVERTISED_LISTENERS": f"PLAINTEXT://localhost:{self._host_port}",
            "KAFKA_CONTROLLER_LISTENER_NAMES": "CONTROLLER",
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP": "PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT",
            "KAFKA_CONTROLLER_QUORUM_VOTERS": "1@localhost:9093",
            "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1",
            "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR": "1",
            "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR": "1",
            "KAFKA_AUTO_CREATE_TOPICS_ENABLE": "true",
            "KAFKA_HEAP_OPTS": "-Xms512m -Xmx512m",
        }
        container = DockerContainer(self.image).with_bind_ports(9092, self._host_port)
        for key, value in env.items():
            container = container.with_env(key, value)
        return container

    def wait_ready(self) -> None:
        self.wait_for_log("Kafka Server started", timeout=120)

    def configure(self) -> None:
        self.config.KAFKA.BROKERS_LIST = [f"localhost:{self._host_port}"]


@ContainerManager.register
class TemporalTestContainer(TestContainer):
    """Temporal dev server (embedded SQLite)."""

    name = "temporal"

    def build(self) -> Any:
        from testcontainers.core.container import DockerContainer

        return (
            DockerContainer(self.image)
            .with_exposed_ports(7233)
            .with_command("server start-dev --namespace default --db-filename /tmp/temporal.db --ip 0.0.0.0")
            .with_env("GOMEMLIMIT", "256MiB")
        )

    def wait_ready(self) -> None:
        self.wait_for_log("CLI", timeout=60)

    def configure(self) -> None:
        temporal = self.config.TEMPORAL
        temporal.HOST, temporal.PORT = self.host(), self.port(7233)
        temporal.NAMESPACE = "default"


@ContainerManager.register
class MinioTestContainer(TestContainer):
    name = "minio"

    def build(self) -> Any:
        from testcontainers.minio import MinioContainer

        return MinioContainer(image=self.image).with_env("GOMEMLIMIT", "192MiB")

    def configure(self) -> None:
        minio = self.config.MINIO
        minio.ENDPOINT = f"{self.host()}:{self.port(9000)}"
        minio.ACCESS_KEY = self.container.access_key
        minio.SECRET_KEY = self.container.secret_key
        minio.SECURE = False


@ContainerManager.register
class ElasticsearchTestContainer(TestContainer):
    name = "elasticsearch"

    @property
    def image(self) -> str:
        return self.config.ELASTIC__IMAGE

    def build(self) -> Any:
        from testcontainers.elasticsearch import ElasticSearchContainer

        return (
            ElasticSearchContainer(image=self.image)
            .with_env("ES_JAVA_OPTS", "-Xms512m -Xmx512m")
            .with_env("discovery.type", "single-node")
        )

    def configure(self) -> None:
        self.config.ELASTIC.HOSTS = [f"http://{self.host()}:{self.port(9200)}"]


@ContainerManager.register
class KeycloakTestContainer(TestContainer):
    name = "keycloak"

    def build(self) -> Any:
        from testcontainers.keycloak import KeycloakContainer

        keycloak = self.config.KEYCLOAK
        return (
            KeycloakContainer(
                image=self.image,
                username=keycloak.ADMIN_USERNAME or "admin",
                password=keycloak.ADMIN_PASSWORD or "admin",
            )
            .with_command("start-dev")
            .with_env("JAVA_OPTS_KC_HEAP", "-Xms64m -Xmx256m")
        )

    def configure(self) -> None:
        keycloak = self.config.KEYCLOAK
        keycloak.SERVER_URL = f"http://{self.host()}:{self.port(8080)}"
        keycloak.ADMIN_USERNAME = self.container.username
        keycloak.ADMIN_PASSWORD = self.container.password


@ContainerManager.register
class VaultTestContainer(TestContainer):
    name = "vault"

    def build(self) -> Any:
        from testcontainers.vault import VaultContainer

        return VaultContainer(image=self.image)

    def configure(self) -> None:
        vault = self.config.VAULT
        vault.ADDR = f"http://{self.host()}:{self.port(8200)}"
        vault.TOKEN = self.container.root_token
        vault.AUTH_METHOD = "token"
        vault.VERIFY_SSL = False
        vault.MOUNT_POINT = "secret"


@ContainerManager.register
class ScyllaDBTestContainer(TestContainer):
    """Needs `fs.aio-max-nr` >= 1048576 on the Docker host."""

    name = "scylladb"

    def build(self) -> Any:
        from testcontainers.core.container import DockerContainer

        return (
            DockerContainer(self.image)
            .with_exposed_ports(9042)
            .with_command("--smp 1 --memory 750M --overprovisioned 1 --developer-mode 1")
        )

    def wait_ready(self) -> None:
        self.wait_for_log("Starting listening for CQL clients", timeout=180)

    def configure(self) -> None:
        scylla = self.config.SCYLLADB
        scylla.CONTACT_POINTS, scylla.PORT = [self.host()], self.port(9042)
