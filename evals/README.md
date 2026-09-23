# ArchiPy plugin evals

Claude Code eval suite for `claude plugin eval`. Each case runs with and without the plugin; the headline number is
the uplift (Δ). Cases 01–03 stage a minimal ArchiPy app with their `scaffold.sh` (`scaffold_script`), so they need `--scaffold` and
write access. If the runner prints that a case runs against an unstaged workspace, move that case to `case.yaml`
(`context.scaffold_script: scaffold.sh`):

```bash
claude plugin eval . --ablation with-without --scaffold --allow-tools Write Edit --judge-model sonnet --no-publish
```

Pilot one case first (`--case 04-otel-question --runs 1`) to check cost. Results land in `evals/results/`
(git-ignored).

| Case | Should fire | Checks |
|---|---|---|
| `01-redis-cache-adapter` | `scaffold-adapter` | adapter under `repositories/user/adapters/`, no top-level `adapters/`, wraps ArchiPy Redis, `raise ... from e` |
| `02-orders-postgres-domain` | `scaffold-domain` | logic + versioned service created, UoW only in logics |
| `03-wallet-transfer-logic` | `scaffold-logic` | `*_sqlalchemy_atomic_decorator` on the logic, domain error for insufficient funds |
| `04-otel-question` | `archipy-docs` | answer uses `OtelUtils` and `otel` extras, no removed 4.x APIs |
| `05-neg-unrelated-shell` | none | no plugin skill fires on an unrelated shell question |
