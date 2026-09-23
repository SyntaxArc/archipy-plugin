# ArchiPy Reference: Errors

Part of the bundled ArchiPy 5.x consumer reference; see `../reference.md` for the verified version, install, and project layout.

## Errors

- Subclass ArchiPy domain/system/resource errors from `archipy.models.errors`.
- Raise with context: `raise NotFoundError(...) from e`.
- Do not leak raw driver exceptions into services.

Live: https://syntaxarc.github.io/ArchiPy/tutorials/error_handling/
