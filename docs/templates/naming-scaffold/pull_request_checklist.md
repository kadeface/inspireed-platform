## Naming

- [ ] New table/column/index names follow `docs/NAMING_CONVENTIONS.md` and `docs/DECISION_DEFAULTS.md`
- [ ] New API / Schema / frontend DTO fields are `snake_case` (no camelCase aliases)
- [ ] New enum **values** are lowercase `snake_case`; PG enum **type** names use underscores
- [ ] Index/unique names use `ix_` / `uq_` (not ad-hoc `unique_…` or bare names)
- [ ] No new dual-read (`a || b`) or scattered field mappers
- [ ] Frontend local variables remain `camelCase`; only DTO fields are `snake_case`
- [ ] Ran naming checks (if enabled):
  - [ ] `pnpm -C frontend lint` (or eslint on `types/**` + `services/**`)
  - [ ] `python scripts/check_naming.py backend/app --strict`
