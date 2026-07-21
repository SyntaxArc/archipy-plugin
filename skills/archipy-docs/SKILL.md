---
name: archipy-docs
description: >-
  Look up ArchiPy patterns for app teams. Use bundled reference.md first, then
  live docs URLs. Trigger when the user asks how to use ArchiPy (config, adapters,
  helpers, errors, DI, project layout).
---

# ArchiPy Docs Lookup

## Procedure

1. Read `reference.md` in this skill directory.
2. Answer from the reference when possible (cite section names).
3. If the topic is missing or version-sensitive, point to the matching live doc:

| Topic             | URL                                                                    |
|-------------------|------------------------------------------------------------------------|
| Docs home         | https://syntaxarc.github.io/ArchiPy/                                   |
| Quickstart        | https://syntaxarc.github.io/ArchiPy/getting-started/quickstart/        |
| Project structure | https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/ |
| Adapters          | https://syntaxarc.github.io/ArchiPy/tutorials/adapters/                |
| Helpers           | https://syntaxarc.github.io/ArchiPy/tutorials/helpers/                 |
| Config            | https://syntaxarc.github.io/ArchiPy/tutorials/config_management/       |
| DI                | https://syntaxarc.github.io/ArchiPy/tutorials/dependency_injection/    |
| Errors            | https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/          |
| API reference     | https://syntaxarc.github.io/ArchiPy/api_reference/                     |

4. Prefer PyPI `archipy` APIs — do not assume the ArchiPy monorepo is on disk.

## Output

- Short, actionable answer with a code sketch when useful
- Link to live docs for deep dives
- Suggest the matching `/scaffold-*` or `/docs-*` command when scaffolding is the next step
