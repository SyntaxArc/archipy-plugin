# ArchiPy Plugin — Agent Instructions

Works in **Cursor** and **Claude Code**.

Consumer plugin for **apps that depend on** PyPI [`archipy`](https://pypi.org/project/archipy/).

**Not** for maintaining the ArchiPy library (no library changelog or core monorepo tooling).

## Essentials

- Python **3.14+**, package manager **`uv`**
- Call flow: `services → logics (atomic UoW) → repositories → adapters → ArchiPy`
- Import direction: `configs ← models ← helpers ← repositories / logics / services`

## Prefer plugin entry points

| Need                            | Command / skill                                                                                                                                      |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| New app tree                    | `/scaffold-app`                                                                                                                                      |
| Full domain slice               | `/scaffold-domain`                                                                                                                                   |
| Models (DTOs / errors)          | `/scaffold-models`                                                                                                                                   |
| Adapter / logic / service / BDD | `/scaffold-adapter`, `/scaffold-logic`, `/scaffold-service`, `/scaffold-bdd`                                                                         |
| Helpers                         | `/scaffold-utils`, `/scaffold-decorator`, `/scaffold-interceptor`                                                                                    |
| Redis search                    | `/redis-search` (full-text, vector, caching)                                                                                                         |
| Health checks                   | `/scaffold-health-checks`, `/docs-health-checks`                                                                                                     |
| OpenTelemetry                   | `/scaffold-observability`, `/docs-observability`                                                                                                     |
| Docs                            | `/docs-quickstart`, `/docs-adapters`, `/docs-helpers`, `/docs-config`, `/docs-errors`, `/docs-testing`, `/docs-observability`, `/docs-health-checks` |

Bundled cheat sheet: `skills/archipy-docs/reference.md`.

When a command names a skill, read that skill's `SKILL.md` in full before generating files. Resolve
`skills/*/reference/` templates from the plugin installation (`$CURSOR_PLUGIN_ROOT` or `$CLAUDE_PLUGIN_ROOT`), copy
them into the app, and never edit plugin templates in place.

Live docs: https://syntaxarc.github.io/ArchiPy/

## Hard rules (apps)

- Models: data only. Logics: UoW + business rules. Services: thin transport.
- Domain adapters under `repositories/{domain}/adapters/` — not a top-level app `adapters/` package.
- FastAPI/uvicorn from `config.FASTAPI`; prefer `AppUtils.create_fastapi_app` / gRPC factories.
- Specific exceptions; always `raise ... from e`.
- Python 3.14 typing, double quotes, Google docstrings, complete public annotations; follow app tooling when stricter.
- No hardcoded secrets or logged credentials/tokens; parameterize queries and justify narrow security suppressions.

## Rule index

- Ownership/precedence: `rules/rules-index-for-apps.mdc`
- Always-on: `architecture-for-apps.mdc`, `python-code-style-for-apps.mdc`, `security-for-apps.mdc`,
  `tooling-for-apps.mdc`, `contributing-for-apps.mdc`
- Python typing: `typing-for-apps.mdc`
- Layers: `using-archipy-models.mdc`, `using-archipy-adapters.mdc`, `using-archipy-repositories.mdc`,
  `using-archipy-logics.mdc`, `using-archipy-services.mdc`
- Support/config: `using-archipy-utils.mdc`, `using-archipy-decorators.mdc`, `using-archipy-interceptors.mdc`,
  `config-and-di.mdc`
- Tests: `testing-bdd-for-apps.mdc`
