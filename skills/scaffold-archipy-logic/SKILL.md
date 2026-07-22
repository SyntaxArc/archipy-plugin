---
name: scaffold-archipy-logic
description: >-
  Scaffold an ArchiPy logic class with unit-of-work decorator and domain DTO
  I/O. Use when adding a use-case under logics/{domain}/.
---

# Scaffold ArchiPy Logic

## Before writing files

Ask the user for:

1. Domain name (e.g. `user`)
2. Logic name / file stem (e.g. `user_registration` → `user_registration_logic.py`)
3. Sync or async atomic (default sync if `postgres-sqlalchemy`; async if `postgres-sqlalchemy-async`)

## Prefer ArchiPy

```bash
uv add "archipy[postgres-sqlalchemy]"
# or: uv add "archipy[postgres-sqlalchemy-async]"
```

## Generate

```text
logics/<domain>/
└── <name>_logic.py
```

Stub shape:

- Google-style class/method docstrings; double quotes; `X | Y` typing.
- Constructor injects the domain repository (or port) — do not construct adapters.
- Public method: domain `*InputDTO` in → domain `*OutputDTO` out.
- Decorate with `postgres_sqlalchemy_atomic_decorator` or `async_postgres_sqlalchemy_atomic_decorator`.

```python
from archipy.helpers.decorators.sqlalchemy_atomic import postgres_sqlalchemy_atomic_decorator


class UserRegistrationLogic:
    """Handles user registration within a single database transaction."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    @postgres_sqlalchemy_atomic_decorator
    def register_user(self, input_dto: UserRegistrationInputDTO) -> UserRegistrationOutputDTO:
        """Validate and create a user.

        Args:
            input_dto: Registration data from the service layer.

        Returns:
            Output DTO for the newly created user.
        """
        ...
```

Create missing domain DTO stubs under `models/dtos/<domain>/domain/v1/` if they do not exist.

## Constraints

- No FastAPI / gRPC imports.
- May call other domain logics; **never** another domain’s repository.
- No `@atomic` on repositories or services — only logics.
- Wire via DI in `configs/containers.py`.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
