---
name: scaffold-archipy-domain
description: >-
  Scaffold a full ArchiPy domain slice (DTOs, errors, repository adapters,
  logic, service). Use when adding a new domain to an existing ArchiPy app.
---

# Scaffold ArchiPy Domain

## Before writing files

1. Inspect `pyproject.toml`, the package tree, neighboring domains, DI containers, and existing tests.
2. Infer package name, installed extras, naming, transport, and sync/async style from the repository.
3. Ask only for unresolved choices that materially change the generated slice:
   - Domain name
   - Missing infrastructure/extras
   - Transport when the app does not already establish one (default FastAPI)
4. Preserve existing files. Extend compatible modules; stop and explain conflicts instead of overwriting them.

## Compose — do not fork templates

Before generating files, read these plugin skills in full:

- `../scaffold-archipy-adapter/SKILL.md`
- `../scaffold-archipy-logic/SKILL.md`
- `../scaffold-archipy-service/SKILL.md`

Apply their constraints and `Verify` sections in order; do not replace them with summaries:

1. **Models** — stubs below, then flesh via `using-archipy-models` rule
2. **scaffold-archipy-adapter** — thin wrapper under `repositories/<domain>/adapters/` + `<domain>_repository.py`
3. **scaffold-archipy-logic** — at least one use-case under `logics/<domain>/`
4. **scaffold-archipy-service** — `services/<domain>/v1/<domain>_service.py`

Install extras as needed: `uv add "archipy[<extras>]"`.

## Model stubs (create first)

```text
models/
├── dtos/<domain>/
│   ├── domain/v1/
│   │   ├── <domain>_input_dto.py
│   │   └── <domain>_output_dto.py
│   └── repository/
│       └── <domain>_command_dto.py
├── errors/
│   └── <domain>_errors.py
└── entities/                    # optional
    └── <domain>_entity.py
```

Example shapes (`order` → rename):

```python
# models/dtos/order/domain/v1/order_create_input_dto.py
from pydantic import Field

from archipy.models.dtos.base_dtos import BaseDTO


class OrderCreateInputDTO(BaseDTO):
    """Domain input crossing the service → logic boundary."""

    customer_id: str = Field(min_length=1)
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
```

```python
# models/dtos/order/domain/v1/order_create_output_dto.py
from archipy.models.dtos.base_dtos import BaseDTO


class OrderCreateOutputDTO(BaseDTO):
    """Domain output returned to the service layer."""

    order_id: str
    status: str
```

```python
# models/dtos/order/repository/order_create_command_dto.py
from archipy.models.dtos.base_dtos import BaseDTO


class OrderCreateCommandDTO(BaseDTO):
    """Repository write command — mapped from domain input inside the logic."""

    customer_id: str
    sku: str
    quantity: int
```

```python
# models/errors/order_errors.py
from archipy.models.errors import NotFoundError, InvalidArgumentError


class OrderNotFoundError(NotFoundError):
    """Raised when an order cannot be located."""


class OrderInvalidArgumentError(InvalidArgumentError):
    """Raised when order input fails domain validation."""
```

Naming: `*InputDTO` / `*OutputDTO` for domain; `*CommandDTO` / `*QueryDTO` for repository. Prefer ArchiPy `BaseDTO`
and the exported `BaseError` hierarchy. Verify imports against the app's installed ArchiPy version before writing.

## Outcome checklist

- [ ] Domain + repository DTOs with ArchiPy naming (`*InputDTO`, `*CommandDTO`, …)
- [ ] Domain error subclassing ArchiPy `BaseError` hierarchy
- [ ] `repositories/<domain>/adapters/` + repository orchestrator
- [ ] One logic with `@postgres_sqlalchemy_atomic_decorator` when Postgres SQLAlchemy is in play
- [ ] One service v1 (FastAPI router or gRPC servicer)
- [ ] DI notes in `configs/containers.py`: ports → adapters → repository → logic → service

## Constraints

- Call flow: `services → logics → repositories → adapters → ArchiPy`.
- Cross-domain: logics may call other logics; never another domain’s repository.
- Double quotes, Google-style docstrings, Python 3.14+ typing.
- Do **not** invent a top-level app `adapters/` package.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Run targeted domain tests; add a focused test when behavior, mapping, or error handling was added.
3. Confirm imports and DI wiring resolve without constructing production infrastructure.
4. Report created/updated files, dependency changes, and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
- Bundled: `../archipy-docs/reference.md`
