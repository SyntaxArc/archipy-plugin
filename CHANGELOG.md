# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Rules for models, logics, services, and BDD (`features/`) — 10 rules total
- AppUtils FastAPI/gRPC bootstrap guidance (`create_fastapi_app`, `create_grpc_app`, `create_async_grpc_app`)
- FastAPIConfig / uvicorn binding rules (`SERVE_HOST`, `SERVE_PORT`, `RELOAD`, `PROXY_HEADERS`)

### Changed

- Enriched always-on architecture rule: call flow, logics/services, cross-domain + UoW
- Tightened adapters (specific boundary errors), decorators (UoW on logics), interceptors (prefer AppUtils), config (DI wire order + `FASTAPI`)
- Synced README rules table/deep-dive and `skills/archipy-docs/reference.md`
- Use official ArchiPy `logo.jpg` as the plugin logo

## [0.1.0] - 2026-07-21

### Added

- Initial Cursor plugin for ArchiPy app teams
- Six consumer-facing rules (architecture, adapters, utils, decorators, interceptors, config/DI)
- Six skills: scaffold app/adapter/utils/decorator/interceptor plus docs lookup with bundled reference
- Nine slash commands for scaffolding and docs navigation
- Complete README for local, team marketplace, and Cursor Marketplace install paths
