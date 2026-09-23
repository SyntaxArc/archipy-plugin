---
type: llm
focus: trace
---
- The unit of work is a real `*_sqlalchemy_atomic_decorator` (for example `postgres_sqlalchemy_atomic_decorator`) applied in `logics/`, not in services or repositories, and no decorator named plain `atomic` is used.
- The service module only maps request DTOs to the logic and back; it contains no SQL or business rules.
- The logic module does not import FastAPI.
