# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-07-28

### Fixed

- Extras names: `postgres-sqlalchemy(-async)` → published `postgres`, `sqlalchemy`, `sqlalchemy-async`
- Symbol names: `JWTUtils`, `ttl_cache_decorator`, `_decorator` suffixes, `capture_span` / `capture_transaction`,
  `grpc_rate_limit_decorator`
- Utils import guidance: use full submodule paths (package `__init__` does not re-export)
- `@atomic` shorthand clarified — real API is `*_sqlalchemy_atomic_decorator`
- `redis-search` rewritten on `RedisAdapter.search_index()` / search DTOs (no raw `client.ft()` templates);
  fixed broken `ensure_index` and undefined domain error
- gRPC health: `""` / `"readiness"` start `NOT_SERVING` until warm-up

### Changed

- Progressive disclosure: BDD / health-checks / redis-search templates moved under skill `reference/`
- Trimmed always-on `architecture-for-apps.mdc` layer dumps; shortened hook `HARD_RULES`
- Narrowed adapters glob to `**/repositories/**/adapters/**/*.py`; anchored models globs; unquoted rule globs
- Hook warning wording for non-repository `adapters/` paths
- Expanded `archipy-docs/reference.md` to all published extras + SessionManagerRegistry, atomic family,
  entities, pagination DTOs, utils facade, rate-limit/metric interceptors, Observability; health labeled as
  plugin convention

### Added

- Extended `scripts/check_catalog.py`: rules table, command→skill refs, logo path, manifest parity,
  CHANGELOG version, skill descriptions
- `tests/` for catalog + hygiene scripts
- CI: Python 3.14, unit tests, markdown link check
- Issue/PR templates, Dependabot

## [0.6.0] - 2026-07-28

### Added

- Command: `/redis-search` (was skill-only; now slash entry matches `AGENTS.md`)
- Concrete stubs in `redis-search`, `scaffold-archipy-domain` (DTO/error), and helper skills (utils / decorator / interceptor)
- `scripts/check_catalog.py` + GitHub Actions CI for version/catalog sync
- `hooks/hooks.json` + `scripts/scaffold_hygiene.py` (session hard-rules context; warn on top-level `adapters/`)
- `CONTRIBUTING.md` for this plugin (dual IDE version bump + catalog checklist)

### Changed

- README catalog: Skills (12), Commands (19); docs map includes redis-search and health
- Decorator skill/command: `postgres_sqlalchemy_atomic_decorator` (replace legacy `sqlalchemy_atomic` wording)
- `archipy-docs` topic table: Testing, Observability, Redis search
- Health skill + config rule point at `reference.md` for canonical BaseConfig / health probe prose

## [0.5.0] - 2026-07-27

### Added

- Skills: `scaffold-archipy-health-checks` (FastAPI HTTP probes and gRPC `grpc.health.v1` Health servicer)
- Commands: `/scaffold-health-checks`, `/docs-health-checks`
- Docs lookup: bundled `reference.md` health-check guidance (HTTP + gRPC) + `archipy-docs` topic row
- Consumer catalog updates in `AGENTS.md` and `README.md`

## [0.4.0] - 2026-07-25

### Added

- Skill: `redis-search` for RediSearch full-text, vector search, and search-caching adapters
- Consumer pointers for Redis search in `AGENTS.md`

## [0.3.0] - 2026-07-25

### Added

- Claude Code support via `.claude-plugin/` manifest and marketplace catalog
- Cursor `.cursor-plugin/marketplace.json` for multi-plugin discovery

### Changed

- Renamed repository from `archipy-cursor-plugin` to `archipy-plugin`
- README install paths for Cursor local symlink and Claude Code marketplace

## [0.2.0] - 2026-07-21

### Added

- Skills: `scaffold-archipy-logic`, `scaffold-archipy-service`, `scaffold-archipy-domain`, `scaffold-archipy-bdd`
- Commands: `/scaffold-logic`, `/scaffold-service`, `/scaffold-domain`, `/scaffold-bdd`, `/docs-errors`,
  `/docs-testing`, `/docs-observability`
- Rule: `using-archipy-repositories.mdc`
- `AGENTS.md` consumer one-pager
- Extras matrix and scaffold pointers in `skills/archipy-docs/reference.md`
- Rules for models, logics, services, and BDD (`features/`)
- AppUtils FastAPI/gRPC bootstrap guidance and FastAPIConfig / uvicorn binding rules

### Changed

- `scaffold-archipy-app` emits `manage.py` + `AppUtils` / `FASTAPI` when FastAPI is requested
- Services rule globs include `**/manage.py`
- Models rule points at AppUtils FastAPI error → HTTP mapping
- Enriched architecture rule; tightened adapters/decorators/interceptors/config
- README tables for 11 rules, 10 skills, 16 commands
- Use official ArchiPy `logo.jpg` as the plugin logo
- `/scaffold-bdd` embeds consumer templates for `scenario_context`, pool manager, `environment`, optional
  `test_containers` (ArchiPy-pattern, slim — no core gRPC/Temporal bootstrap)

## [0.1.0] - 2026-07-21

### Added

- Initial Cursor plugin for ArchiPy app teams
- Six consumer-facing rules (architecture, adapters, utils, decorators, interceptors, config/DI)
- Six skills: scaffold app/adapter/utils/decorator/interceptor plus docs lookup with bundled reference
- Nine slash commands for scaffolding and docs navigation
- Complete README for local, team marketplace, and Cursor Marketplace install paths
