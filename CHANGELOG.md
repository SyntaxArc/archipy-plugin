# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-21

### Added

- Skills: `scaffold-archipy-logic`, `scaffold-archipy-service`, `scaffold-archipy-domain`, `scaffold-archipy-bdd`
- Commands: `/scaffold-logic`, `/scaffold-service`, `/scaffold-domain`, `/scaffold-bdd`, `/docs-errors`, `/docs-testing`, `/docs-observability`
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
- `/scaffold-bdd` embeds consumer templates for `scenario_context`, pool manager, `environment`, optional `test_containers` (ArchiPy-pattern, slim — no core gRPC/Temporal bootstrap)

## [0.1.0] - 2026-07-21

### Added

- Initial Cursor plugin for ArchiPy app teams
- Six consumer-facing rules (architecture, adapters, utils, decorators, interceptors, config/DI)
- Six skills: scaffold app/adapter/utils/decorator/interceptor plus docs lookup with bundled reference
- Nine slash commands for scaffolding and docs navigation
- Complete README for local, team marketplace, and Cursor Marketplace install paths
