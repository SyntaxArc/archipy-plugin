# ArchiPy Reference: BDD testing

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## BDD testing

```text
features/
├── *.feature, steps/
├── scenario_context.py
├── scenario_context_pool_manager.py
├── test_helpers.py
├── environment.py
└── test_containers.py   # infra / @needs-* only
```

- Behave (not pytest); `uv add "archipy[behave]"`; infra also `archipy[testcontainers]`.
- Isolate with `ScenarioContext` + pool; hooks in `environment.py` (see `/scaffold-bdd`).
- Tag infra `@needs-*`; skip every `@needs-*` tag present
  (`behave --tags=~@needs-redis --tags=~@needs-postgres`).
- Reset `SessionManagerRegistry` after scenarios.
- Do not copy ArchiPy-core gRPC/Temporal environment blocks unless the app needs them.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
