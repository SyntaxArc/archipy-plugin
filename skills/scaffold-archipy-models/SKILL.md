---
name: scaffold-archipy-models
description: >-
  Scaffold ArchiPy models (domain/repository DTOs, errors, optional entities and
  types). Use when adding data structures under models/ — no I/O, no business
  rules.
---

# Scaffold ArchiPy Models

## Scope

**Only** `models/`. Do not create repositories, logics, services, or helpers here.

## Before writing files

1. Inspect existing `models/` (DTOs, errors, entities, types), neighboring domains, and the installed ArchiPy version.
2. Infer domain name, DTO naming, and error grouping from existing modules.
3. Ask only for unresolved domain / operation names.
4. Preserve existing model modules; do not overwrite.

## Generate

```text
models/
├── dtos/<domain>/
│   ├── domain/v{n}/
│   │   ├── <op>_input_dto.py
│   │   └── <op>_output_dto.py
│   └── repository/
│       ├── <action>_command_dto.py
│       └── <action>_query_dto.py
├── errors/
│   └── <domain>_errors.py
├── entities/                    # optional
│   └── <domain>_entity.py
└── types/                       # optional
    └── <domain>_types.py
```

Naming: `*InputDTO` / `*OutputDTO` for domain (versioned under `domain/v{n}/`); `*CommandDTO` / `*QueryDTO` /
`*ResponseDTO` for repository (never versioned). Prefer ArchiPy `BaseDTO` and the exported `BaseError` hierarchy.
Verify imports against the app's installed ArchiPy version before writing.

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
from archipy.models.errors import InvalidArgumentError, NotFoundError


class OrderNotFoundError(NotFoundError):
    """Raised when an order cannot be located."""


class OrderInvalidArgumentError(InvalidArgumentError):
    """Raised when order input fails domain validation."""
```

`BaseDTO` is frozen — do not mutate instances after validation. Prefer existing ArchiPy errors over near-duplicates.
Export public app errors from `models/errors/__init__.py` when other layers consume them. Prefer ArchiPy pagination /
sort / search DTOs before inventing page or cursor shapes.

## Constraints

- Data structures only — no I/O, no business rules, no adapters, no DB sessions, no HTTP/gRPC types.
- Never import repositories, logics, or services from models.
- Do not version repository DTOs.
- Double quotes, Google-style docstrings, Python 3.14+ typing.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Confirm DTO naming, versioned domain vs unversioned repository layout, and error subclassing.
3. Import the new modules without constructing infrastructure.
4. Report files and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
- https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/
- Bundled: `../archipy-docs/reference.md` (DTO naming)
