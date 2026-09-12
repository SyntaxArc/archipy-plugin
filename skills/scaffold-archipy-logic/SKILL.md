---
name: scaffold-archipy-logic
description: >-
  Scaffold an ArchiPy logic class with unit-of-work decorator and domain DTO
  I/O. Use when adding a use-case under logics/{domain}/.
---

# Scaffold ArchiPy Logic

## Before writing files

1. Inspect the target domain's DTOs, repository contract, neighboring logics, DI wiring, and tests.
2. Infer naming and sync/async style from existing code and installed extras.
3. Ask only for an unresolved domain/use-case name or transaction choice. Default to sync for
   `postgres` + `sqlalchemy` and async for `postgres` + `sqlalchemy-async`. Skip a UoW decorator when the
   use-case does not own a SQLAlchemy session.
4. Preserve existing use cases; do not overwrite logic or DTO files.

## Prefer ArchiPy

Install a SQLAlchemy extra only when this use-case owns a Postgres UoW:

```bash
uv add "archipy[postgres,sqlalchemy]"
# or: uv add "archipy[postgres,sqlalchemy-async]"
```

Skip this for Redis/Kafka/other logics that do not wrap a SQLAlchemy session.

## Generate

```text
logics/<domain>/
└── <name>_logic.py
```

Stub shape:

- Google-style class/method docstrings; double quotes; `X | Y` typing.
- Constructor injects the domain repository (or port) — do not construct adapters.
- Public method: domain `*InputDTO` in → domain `*OutputDTO` out.
- Decorate with `postgres_sqlalchemy_atomic_decorator` or `async_postgres_sqlalchemy_atomic_decorator`
  **when Postgres SQLAlchemy is in play**. Otherwise omit the UoW decorator.

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

If domain DTOs or errors are missing, follow `../scaffold-archipy-models/SKILL.md` — do not invent naming.

## Constraints

- No FastAPI / gRPC imports.
- May call other domain logics; **never** another domain’s repository.
- No atomic / UoW decorators on repositories or services — only logics.
- Wire via DI in `configs/containers.py`.

## Verify

1. Run the repository's formatter and linter on generated Python.
2. Add or run focused tests for success, business-rule failure, and rollback-relevant failure.
3. Confirm DTO boundaries, repository injection, decorator choice, and DI wiring.
4. Report files and commands run.

## Docs

- https://syntaxarc.github.io/ArchiPy/getting-started/concepts/
- https://syntaxarc.github.io/ArchiPy/getting-started/project_structure/
