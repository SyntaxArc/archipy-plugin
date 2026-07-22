# ArchiPy Cursor Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ArchiPy Docs](https://img.shields.io/badge/docs-ArchiPy-blue.svg)](https://syntaxarc.github.io/ArchiPy/)
[![ArchiPy](https://img.shields.io/badge/library-SyntaxArc%2FArchiPy-0F172A.svg)](https://github.com/SyntaxArc/ArchiPy)

Cursor rules, skills, and slash commands for **application teams that build
with [ArchiPy](https://github.com/SyntaxArc/ArchiPy)**.

> Marketplace listing: submit this repository
> at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Update this badge once the plugin is
> approved.

## What this is

This plugin helps Cursor agents follow ArchiPy clean-architecture patterns when working in **your** service repos: layer
boundaries, adapters, helpers (utils / decorators / interceptors), configuration, and DI.

It ships:

- **Rules** — persistent guidance while editing matching files
- **Skills** — agent workflows for scaffolding and docs lookup
- **Commands** — slash entry points (`/scaffold-app`, `/docs-helpers`, …)

It is **not** for maintaining the ArchiPy library itself (no graphify, library changelog, or core BDD internals).

## Requirements

- [Cursor](https://cursor.com/) with plugin support
- Apps targeting **Python 3.14+**
- [`uv`](https://docs.astral.sh/uv/) package manager
- PyPI package [`archipy`](https://pypi.org/project/archipy/) (install the extras your service needs)

## Install

### Local (development / personal)

```bash
# From a clone of this repo:
mkdir -p ~/.cursor/plugins/local
ln -sfn "$(pwd)" ~/.cursor/plugins/local/archipy
```

Then run **Developer: Reload Window** in Cursor (or restart Cursor).

Verify under **Customize** that the `archipy` plugin loaded (rules, skills, commands).

### Team marketplace (Teams / Enterprise)

1. Open **Dashboard → Plugins → Team Marketplaces**
2. **Import from Repo** and point at `https://github.com/SyntaxArc/archipy-cursor-plugin`
3. Set access and install mode (Default Off / Default On / Required)

### Cursor Marketplace

1. After this plugin is listed, open **Customize** or [cursor.com/marketplace](https://cursor.com/marketplace)
2. Search for **archipy** and install
3. Optionally scope install to the current workspace

Until listing is approved, use **Local** or **Team marketplace** install.

## What’s included

### Rules (11)

| Rule file                        | Applies when                         |
|----------------------------------|--------------------------------------|
| `architecture-for-apps.mdc`      | Always                               |
| `using-archipy-adapters.mdc`     | `**/adapters/**/*.py`                |
| `using-archipy-utils.mdc`        | `**/helpers/utils/**/*.py`           |
| `using-archipy-decorators.mdc`   | `**/helpers/decorators/**/*.py`      |
| `using-archipy-interceptors.mdc` | `**/helpers/interceptors/**/*.py`    |
| `config-and-di.mdc`              | `**/configs/**/*.py`                 |
| `using-archipy-models.mdc`       | `**/models/**/*.py`                  |
| `using-archipy-repositories.mdc` | `**/repositories/**/*.py`            |
| `using-archipy-logics.mdc`       | `**/logics/**/*.py`                  |
| `using-archipy-services.mdc`     | `**/services/**/*.py`, `**/manage.py` |
| `testing-bdd-for-apps.mdc`       | `**/features/**/*`                   |

### Skills (10)

| Skill                          | When to use                                                               |
|--------------------------------|---------------------------------------------------------------------------|
| `scaffold-archipy-app`         | Bootstrap a new ArchiPy-based service layout                              |
| `scaffold-archipy-domain`      | Full domain slice (models, repo, logic, service)                          |
| `scaffold-archipy-adapter`     | Add domain adapter under `repositories/{domain}/adapters/`                |
| `scaffold-archipy-logic`       | Use-case under `logics/{domain}/` with `@atomic`                          |
| `scaffold-archipy-service`     | Thin FastAPI/gRPC service under `services/{domain}/v{n}/`                 |
| `scaffold-archipy-bdd`         | Behave `features/` stub                                                   |
| `scaffold-archipy-utils`       | Wire or create `helpers/utils`                                            |
| `scaffold-archipy-decorator`   | Wire or create `helpers/decorators`                                       |
| `scaffold-archipy-interceptor` | Wire or create `helpers/interceptors`                                     |
| `archipy-docs`                 | Answer “how do I… with ArchiPy?” using bundled `reference.md` + live docs |

### Commands (16)

| Command                 | Action                            |
|-------------------------|-----------------------------------|
| `/scaffold-app`         | Run scaffold-archipy-app          |
| `/scaffold-domain`      | Run scaffold-archipy-domain       |
| `/scaffold-adapter`     | Run scaffold-archipy-adapter      |
| `/scaffold-logic`       | Run scaffold-archipy-logic        |
| `/scaffold-service`     | Run scaffold-archipy-service      |
| `/scaffold-bdd`         | Run scaffold-archipy-bdd          |
| `/scaffold-utils`       | Run scaffold-archipy-utils        |
| `/scaffold-decorator`   | Run scaffold-archipy-decorator    |
| `/scaffold-interceptor` | Run scaffold-archipy-interceptor  |
| `/docs-quickstart`      | Quickstart + bundled reference    |
| `/docs-adapters`        | Adapter patterns + docs links     |
| `/docs-helpers`         | Utils / decorators / interceptors |
| `/docs-config`          | BaseConfig + DI docs              |
| `/docs-errors`          | Error handling docs               |
| `/docs-testing`         | BDD testing docs                  |
| `/docs-observability`   | Observability docs                |

There is **no** `/scaffold-helper` — use the three helper-specific commands.

## Quick start

1. Install the plugin locally (symlink above) and reload Cursor.
2. Open an application workspace (empty or existing Python service).
3. In Agent chat, run `/scaffold-app` — answer package name and extras (e.g. `redis`).
4. Run `/docs-quickstart` to confirm config + first adapter steps.
5. Expect: `AppConfig`, models stub, `repositories/<domain>/`, optional `manage.py` (if `fastapi`), helpers tree, `.env.example`.

## Commands deep dive

### `/scaffold-app`

- **Purpose:** Create a minimal ArchiPy app package tree.
- **Asks:** Package name, extras, optional first domain.
- **Outcome:** `configs/app_config.py`, models stub, `repositories/<domain>/`, optional helpers, `manage.py` when FastAPI, `.env.example`.

### `/scaffold-domain`

- **Purpose:** Full domain slice composing models + adapter + logic + service.
- **Asks:** Domain, extras, transport.
- **Outcome:** DTOs/errors, repository adapters, one logic, one service v1, DI notes.

### `/scaffold-adapter`

- **Purpose:** Add a domain adapter under the domain repository.
- **Asks:** Domain, purpose, sync/async, mocks yes/no, wrap ArchiPy vs new client.
- **Outcome:** `repositories/<domain>/adapters/<domain>_<purpose>_adapter.py` (+ repository stub if missing).

### `/scaffold-logic`

- **Purpose:** Use-case class with unit-of-work decorator.
- **Asks:** Domain, logic name, sync/async atomic.
- **Outcome:** `logics/<domain>/<name>_logic.py`.

### `/scaffold-service`

- **Purpose:** Thin FastAPI router or gRPC servicer.
- **Asks:** Domain, version, FastAPI vs gRPC.
- **Outcome:** `services/<domain>/v{n}/<domain>_service.py` + AppUtils bootstrap notes.

### `/scaffold-bdd`

- **Purpose:** Behave feature layout with ScenarioContext isolation.
- **Asks:** Feature name; mocks vs `@needs-*` infra.
- **Outcome:** `scenario_context.py`, pool manager, `test_helpers.py`, `environment.py`, feature/steps; infra adds slim `test_containers.py` + `.env.test`.

### `/scaffold-utils`

- **Purpose:** Prefer ArchiPy utils; otherwise scaffold a pure util.
- **Asks:** Purpose; built-in vs custom.
- **Outcome:** Usage snippet or `helpers/utils/<name>_utils.py`.

### `/scaffold-decorator`

- **Purpose:** Prefer ArchiPy decorators (`ttl_cache`, atomic, tracing, …).
- **Asks:** Purpose; sync/async; built-in vs custom.
- **Outcome:** Usage snippet or `helpers/decorators/<name>.py` with example.

### `/scaffold-interceptor`

- **Purpose:** Prefer ArchiPy FastAPI/gRPC interceptors; custom stays cross-cutting.
- **Asks:** Framework; sync/async; built-in vs custom.
- **Outcome:** Interceptor module + wiring notes (DI / framework).

### `/docs-quickstart` / `/docs-adapters` / `/docs-helpers` / `/docs-config` / `/docs-errors` / `/docs-testing` / `/docs-observability`

- **Purpose:** Orient the agent on the matching topic using `skills/archipy-docs/reference.md` first, then live docs
  URLs.
- **Outcome:** Short guidance + links; may suggest a `/scaffold-*` follow-up.

## Rules deep dive

### `architecture-for-apps`

Always-on layer map, call flow (`services → logics → repositories → adapters`), and one-way imports.

- **Do:** Keep models free of I/O; UoW on logics; cross-domain via logics only.
- **Don’t:** Import repositories/adapters from `models/`; invent a top-level app `adapters/` package.

### `using-archipy-adapters`

Prefer ArchiPy extras and thin domain wrappers under `repositories/{domain}/adapters/`.

- **Do:** Map specific driver errors to domain errors with `raise ... from e`.
- **Don’t:** Mix sync and async in one class; leak raw driver exceptions.

### `using-archipy-utils`

Pure utilities; prefer ArchiPy utils. **AppUtils** for FastAPI/gRPC factories.

- **Do:** Use `create_fastapi_app` / `create_grpc_app` / `create_async_grpc_app`; drive uvicorn from `config.FASTAPI`.
- **Don’t:** Hand-roll bare `FastAPI()` / `grpc.server()`; open DB/Redis clients in utils.

### `using-archipy-decorators`

Prefer ArchiPy decorators; UoW decorators belong on **logics**.

- **Do:** Preserve wrapped signatures (`functools.wraps`); use `postgres_sqlalchemy_atomic_decorator` on logics.
- **Don’t:** Construct adapters inside decorator modules.

### `using-archipy-interceptors`

Cross-cutting hooks only; prefer AppUtils auto-registration for stock interceptors.

- **Do:** Keep interceptors free of use-case writes.
- **Don’t:** Register interceptors by importing them from adapters at module level.

### `config-and-di`

`BaseConfig`, `FastAPIConfig`, `customize()`, DI wire order `ports → adapters → repositories → logics → services`.

- **Do:** Call `BaseConfig.set_global` once; set FastAPI/uvicorn defaults via `config.FASTAPI`.
- **Don’t:** Commit secrets or scatter `os.environ` outside config.

### `using-archipy-models`

DTOs/entities/errors layout and naming (`*InputDTO` / `*CommandDTO` / …).

- **Do:** Version domain DTOs under `domain/v{n}/`; subclass ArchiPy errors.
- **Don’t:** Put I/O or business rules in models.

### `using-archipy-repositories`

Domain data access; adapters under `repositories/{domain}/adapters/`.

- **Do:** Orchestrate in `{domain}_repository.py`; map to repository DTOs; isolate domains.
- **Don’t:** Call another domain’s repository; put `@atomic` here.

### `using-archipy-logics`

Business rules + unit of work; domain isolation.

- **Do:** Domain DTO in/out; `@atomic` on public methods; call other logics for cross-domain.
- **Don’t:** Import another domain’s repository; import FastAPI/gRPC.

### `using-archipy-services`

Thin transport; AppUtils bootstrap; uvicorn from `FastAPIConfig`.

- **Do:** Map errors to HTTP/gRPC status; version routers under `v{n}/`.
- **Don’t:** Put `@atomic` or business rules in services; hardcode host/port.

### `testing-bdd-for-apps`

Behave + `ScenarioContext`; inject ports/mocks; `@needs-*` infra tags.

- **Do:** Isolate scenarios; swap mocks via DI/context.
- **Don’t:** Share mutable globals across scenarios; use pytest as the primary style.

## Project layout

```text
archipy-cursor-plugin/
├── .cursor-plugin/
│   └── plugin.json          # Plugin manifest (name: archipy)
├── rules/                   # .mdc rules
├── skills/                  # SKILL.md directories (+ docs reference)
├── commands/                # Slash commands
├── assets/logo.jpg
├── AGENTS.md
├── README.md
├── LICENSE
└── CHANGELOG.md
```

Cursor discovers `rules/`, `skills/`, and `commands/` automatically when the manifest does not override paths.

## ArchiPy docs map

| Plugin entry                                 | Live documentation                                                                                                                                                         |
|----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/docs-quickstart`, `scaffold-archipy-app`   | [Quickstart](https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/), [Project structure](https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/) |
| `/docs-adapters`, `scaffold-archipy-adapter` | [Adapters](https://syntaxarc.github.io/ArchiPy/tutorials/adapters/), [API adapters](https://syntaxarc.github.io/ArchiPy/api_reference/adapters/)                           |
| `/docs-helpers`, helper scaffolds            | [Helpers](https://syntaxarc.github.io/ArchiPy/tutorials/helpers/), [Observability](https://syntaxarc.github.io/ArchiPy/tutorials/observability/)                           |
| `/docs-config`                               | [Config](https://syntaxarc.github.io/ArchiPy/tutorials/config_management/), [DI](https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/)                      |
| `/docs-errors`                               | [Error handling](https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/)                                                                                             |
| `/docs-testing`, `scaffold-archipy-bdd`      | [Testing strategy](https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/)                                                                                         |
| `/docs-observability`                        | [Observability](https://syntaxarc.github.io/ArchiPy/tutorials/observability/)                                                                                               |
| `archipy-docs` / `reference.md`              | [Docs home](https://syntaxarc.github.io/ArchiPy/), [API reference](https://syntaxarc.github.io/ArchiPy/api_reference/)                                                     |

## Developing / contributing

1. Clone this repo and symlink it to `~/.cursor/plugins/local/archipy`.
2. Edit rules (`.mdc` frontmatter: `description`, `alwaysApply` / `globs`), skills (`name` + `description` matching
   folder name), or commands (`name` + `description`).
3. Reload the Cursor window after changes.
4. Keep consumer focus: apps using PyPI `archipy`, not ArchiPy monorepo maintainers.
5. Open a PR with a clear summary; update `CHANGELOG.md` for user-facing changes.
6. Bump `version` in `.cursor-plugin/plugin.json` when publishing a release.

## Marketplace / security

- This repository is **open source** (MIT).
- v0.2 ships **no MCP servers** and **no plugin variables / secrets**.
- Cursor Marketplace submissions are **manually reviewed**; updates are re-reviewed.
- Do not add API tokens or credentials to the plugin tree.

Publish: [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish)

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE) © SyntaxArc

## Related

- [ArchiPy library](https://github.com/SyntaxArc/ArchiPy) — Python package (Apache-2.0)
- [ArchiPy documentation](https://syntaxarc.github.io/ArchiPy/)
- Contributing to **ArchiPy core** → use
  the [ArchiPy CONTRIBUTING](https://github.com/SyntaxArc/ArchiPy/blob/master/CONTRIBUTING.md) guide
- Contributing to **this plugin** → PRs against this repository
