---
type: llm
focus: trace
---
- The adapter wraps an ArchiPy Redis adapter (for example `RedisAdapter` / `AsyncRedisAdapter` from `archipy.adapters.redis`) rather than building a raw redis client from scratch.
- Driver or client errors are mapped to domain errors with `raise ... from e`; no bare `except:` that swallows errors.
- The adapter contains no business rules (no pricing, permission, or workflow decisions).
