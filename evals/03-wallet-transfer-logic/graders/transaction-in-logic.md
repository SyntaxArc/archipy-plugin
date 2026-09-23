---
type: llm
focus: trace
---
- The transfer is wrapped in a single unit of work via a `*_sqlalchemy_atomic_decorator` on the logic method, so both balance updates commit or roll back together.
- Insufficient balance raises a specific domain error (a subclass of an ArchiPy error), not a bare `Exception`.
- The logic calls repositories, not database sessions or adapters directly.
