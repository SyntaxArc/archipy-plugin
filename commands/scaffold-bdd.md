---
name: scaffold-bdd
description: Scaffold Behave BDD layout with ScenarioContext, pool manager, environment, optional testcontainers
---

# /scaffold-bdd

Follow the **scaffold-archipy-bdd** skill.

1. Ask for feature name and **mocks** vs **infra** (`@needs-*` + testcontainers).
2. Always generate (if missing), modeled on ArchiPy `features/`:
    - `features/scenario_context.py`
    - `features/scenario_context_pool_manager.py`
    - `features/test_helpers.py` (`get_current_scenario_context`)
    - `features/environment.py` (behave hooks + `TestConfig`)
    - `features/<name>.feature` + `features/steps/<name>_steps.py`
3. Infra mode: also `features/test_containers.py` (`ContainerManager` + only needed containers), `.env.test` image vars,
   `uv add "archipy[testcontainers]"`.
4. Do **not** copy ArchiPy-core gRPC/Temporal server bootstrap unless the app tests those.

Docs: https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/
