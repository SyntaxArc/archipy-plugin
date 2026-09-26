"""Runs the real app for BDD: FastAPI through TestClient, gRPC through a real server + channel, Temporal worker.

Build the harness only after the containers are started and patched into the global config: the app's DI container,
engines, and clients bind to whatever endpoints they see at construction time.

Fill in the `ADAPT` hooks below. Always create the app with `AppUtils` (`create_fastapi_app`, `create_grpc_app`,
`create_async_grpc_app`) and register the same routers/servicers as the production entrypoint, so exception handlers,
interceptors, middleware, and lifespan match prod. Never build a bare `FastAPI()` or `grpc.server()` here.
"""

import asyncio
import logging
import threading
from collections.abc import Callable, Coroutine
from typing import Any

import grpc
from fastapi import FastAPI
from fastapi.testclient import TestClient

from features.test_containers import ContainerManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------------------------------
# ADAPT: app hooks. Import app modules inside the functions, never at module top (containers must start first).
# ---------------------------------------------------------------------------------------------------------------------


def build_rest_app() -> FastAPI | None:
    """Create the FastAPI app with `AppUtils` and include the app's routers; None when the app has no REST API."""
    # from archipy.helpers.utils.app_utils import AppUtils
    # from configs.containers import ServiceContainer
    # from services.user.v1.user_service import create_user_v1_router
    #
    # container = ServiceContainer()
    # app = AppUtils.create_fastapi_app()
    # app.include_router(create_user_v1_router(container))  # same routers as manage.create_app()
    # return app
    return None


def build_grpc_server() -> grpc.Server | grpc.aio.Server | None:
    """Create the gRPC server with `AppUtils` and register the app's servicers (no port); None without gRPC."""
    # from archipy.configs.base_config import BaseConfig
    # from archipy.helpers.utils.app_utils import AppUtils
    # from configs.containers import ServiceContainer
    # from services.user.v1.user_grpc_service import register_user_v1_servicers
    #
    # container = ServiceContainer()
    # server = AppUtils.create_grpc_app(BaseConfig.global_config())  # async servicers: create_async_grpc_app
    # register_user_v1_servicers(server, container)
    # return server
    return None


def temporal_worker_spec() -> dict[str, Any] | None:
    """Return `TemporalWorkerManager.start_worker` kwargs for the app's worker; None when Temporal is not in this run."""
    # if "temporal" not in ContainerManager.running():  # e.g. `behave --tags=~@needs-temporal`
    #     return None
    # from archipy.configs.base_config import BaseConfig
    # from workers import WORKFLOWS, create_activities
    # return {
    #     "task_queue": BaseConfig.global_config().TEMPORAL.TASK_QUEUE,
    #     "workflows": WORKFLOWS,
    #     "activities": create_activities(),
    # }
    return None


def prepare_state() -> None:
    """Create the schema once per run: run migrations (e.g. `alembic upgrade head`) or `metadata.create_all`.

    Guard each store with `if "<name>" in ContainerManager.running():` so filtered runs skip absent containers.
    """


def reset_state() -> None:
    """Remove data written by the previous scenario: truncate tables, `FLUSHDB`, delete buckets/indices/topics.

    Guard each store with `if "<name>" in ContainerManager.running():`, as in `prepare_state()`.
    """


# ---------------------------------------------------------------------------------------------------------------------


class BackgroundLoop:
    """An asyncio loop on a daemon thread, for servers and workers that must outlive a single step."""

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self.loop.run_forever, name="bdd-background-loop", daemon=True)
        self._thread.start()

    def run[T](self, coro: Coroutine[Any, Any, T], timeout: float = 60) -> T:
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)

    def close(self) -> None:
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(timeout=10)
        self.loop.close()


class AppHarness:
    """Owns the app under test for one behave run."""

    def __init__(self) -> None:
        self.rest: TestClient | None = None
        self.grpc_target: str | None = None
        self._grpc_server: grpc.Server | grpc.aio.Server | None = None
        self._grpc_channel: grpc.Channel | None = None
        self._worker_manager: Any = None
        self._background: BackgroundLoop | None = None
        self._cleanups: list[Callable[[], None]] = []

    @property
    def background(self) -> BackgroundLoop:
        if self._background is None:
            self._background = BackgroundLoop()
        return self._background

    def start(self) -> None:
        prepare_state()
        self._start_rest()
        self._start_grpc()
        self._start_temporal_worker()

    def _start_rest(self) -> None:
        app = build_rest_app()
        if app is None:
            return
        self.rest = TestClient(app, raise_server_exceptions=False)
        self.rest.__enter__()  # runs the app lifespan (startup/shutdown hooks, OTel)
        self._cleanups.append(lambda: self.rest.__exit__(None, None, None))

    def _start_grpc(self) -> None:
        async def build() -> grpc.Server | grpc.aio.Server | None:
            return build_grpc_server()  # an aio server binds to the loop it is created on

        server = self.background.run(build())
        if server is None:
            return
        if isinstance(server, grpc.aio.Server):
            port = server.add_insecure_port("127.0.0.1:0")
            self.background.run(server.start())
            self._cleanups.append(lambda: self.background.run(server.stop(grace=1)))
        else:
            port = server.add_insecure_port("127.0.0.1:0")
            server.start()
            self._cleanups.append(lambda: server.stop(grace=1).wait())
        self._grpc_server = server
        self.grpc_target = f"127.0.0.1:{port}"
        logger.info("gRPC server listening on %s", self.grpc_target)

    def _start_temporal_worker(self) -> None:
        spec = temporal_worker_spec()
        if spec is None:
            return
        from archipy.adapters.temporal.worker import TemporalWorkerManager

        async def start() -> Any:
            self._worker_manager = TemporalWorkerManager()
            return await self._worker_manager.start_worker(**spec)

        self.background.run(start())
        self._cleanups.append(lambda: self.background.run(self._worker_manager.shutdown_all_workers()))

    def grpc_channel(self) -> grpc.Channel:
        """Sync channel to the app's gRPC server, shared across scenarios. Build stubs from it in steps."""
        if self.grpc_target is None:
            raise RuntimeError("App has no gRPC server; implement build_grpc_server()")
        if self._grpc_channel is None:
            self._grpc_channel = grpc.insecure_channel(self.grpc_target)
            grpc.channel_ready_future(self._grpc_channel).result(timeout=10)
            self._cleanups.append(self._grpc_channel.close)
        return self._grpc_channel

    def async_grpc_channel(self) -> grpc.aio.Channel:
        """New aio channel bound to the calling loop — use inside `async def` steps and close it when done."""
        if self.grpc_target is None:
            raise RuntimeError("App has no gRPC server; implement build_grpc_server()")
        return grpc.aio.insecure_channel(self.grpc_target)

    def reset(self) -> None:
        reset_state()

    def stop(self) -> None:
        for cleanup in reversed(self._cleanups):
            try:
                cleanup()
            except Exception:
                logger.exception("Error stopping app harness component")
        self._cleanups.clear()
        if self._background is not None:
            self._background.close()
            self._background = None
