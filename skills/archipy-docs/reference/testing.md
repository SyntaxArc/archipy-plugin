# ArchiPy Reference: BDD testing

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## BDD testing

```text
features/
├── *.feature, steps/
├── environment.py        # TestConfig(AppConfig) → containers → app harness → per-scenario reset
├── test_containers.py    # ContainerManager, one container per @needs-* tag
├── app_harness.py        # AppUtils-built app: TestClient, real gRPC server + channel, Temporal worker
├── scenario_context.py, scenario_context_pool_manager.py, test_helpers.py
.env.test
```

- Behave (not pytest); `uv add --group dev "archipy[behave,testcontainers]"`.
- Scenarios drive the **services layer** only: REST via FastAPI `TestClient`, gRPC via generated stubs over a real
  channel. The app is created with `AppUtils.create_fastapi_app` / `create_grpc_app` / `create_async_grpc_app`.
- Real infrastructure via testcontainers for everything the app owns (Postgres, MySQL, Redis, Kafka, Temporal, MinIO,
  Elasticsearch, Keycloak, Vault, ScyllaDB); tag features `@needs-*`.
- Containers start before the app is built and live for the whole run; data is reset after each scenario.
- Temporal: the harness runs the app's real worker (`TemporalWorkerManager.start_worker`).
- Only third-party APIs without a container may be faked, at the adapter port via DI.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/ · templates: `/scaffold-bdd`
