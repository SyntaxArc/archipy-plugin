---
name: archipy-docs
description: >-
  Look up ArchiPy patterns for app teams using the bundled 5.x reference and live
  docs. Trigger when the user asks how to use ArchiPy (config, adapters, helpers,
  errors, DI, project layout, observability).
---

# ArchiPy Docs Lookup

## Procedure

1. Determine the app's installed ArchiPy major version from `pyproject.toml` or `uv.lock` when available.
2. For version-sensitive topics (extras, observability, decorators, interceptors), consult the matching live doc first.
3. Read `reference.md` in this skill directory; it targets ArchiPy 5.x. For older apps, explain migration differences
   instead of recommending removed APIs.
4. Answer concisely and link the matching live doc:

| Topic             | URL                                                                                                   |
|-------------------|-------------------------------------------------------------------------------------------------------|
| Docs home         | https://syntaxarc.github.io/ArchiPy/                                                                  |
| Quickstart        | https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/                                       |
| Project structure | https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/                                |
| Adapters          | https://syntaxarc.github.io/ArchiPy/tutorials/adapters/                                               |
| Helpers           | https://syntaxarc.github.io/ArchiPy/tutorials/helpers/                                                |
| Config            | https://syntaxarc.github.io/ArchiPy/tutorials/config_management/                                      |
| DI                | https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/                                   |
| Health checks     | Bundled `reference.md` (HTTP + gRPC) + `/scaffold-health-checks`                                      |
| Models / DTOs     | Bundled `reference.md` § DTO naming + `/scaffold-models`                                              |
| Errors            | https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/ + `/scaffold-models`                     |
| Testing           | https://syntaxarc.github.io/ArchiPy/tutorials/testing_strategy/ + `/scaffold-bdd`                     |
| Observability     | Bundled `reference.md` § Observability + https://syntaxarc.github.io/ArchiPy/tutorials/observability/ |
| Redis search      | Bundled `reference.md` + `/redis-search`                                                              |
| API reference     | https://syntaxarc.github.io/ArchiPy/api_reference/                                                    |

5. Prefer PyPI `archipy` APIs — do not assume the ArchiPy monorepo is on disk.

## Output

- Short, actionable answer with a code sketch when useful
- Link to live docs for deep dives
- Suggest the matching `/scaffold-*` or `/docs-*` command when scaffolding is the next step
