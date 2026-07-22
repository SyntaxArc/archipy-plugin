---
name: scaffold-domain
description: Scaffold a full ArchiPy domain slice (models, repo, logic, service)
---

# /scaffold-domain

Follow the **scaffold-archipy-domain** skill.

1. Ask for domain name, extras, and transport (FastAPI default).
2. Compose adapter + models + logic + service skills for one domain.
3. Note DI wiring: ports → adapters → repository → logic → service.

Docs: https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
