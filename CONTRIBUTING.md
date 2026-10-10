# Contributing

## Workflow

- **Branching:** trunk-based. Branch from `main` as `feat/<issue>-<slug>`,
  `fix/...`, `chore/...`, or `sec/...`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `ci:`, `refactor:`, `chore:`, `perf:`).
- **Pull requests:** link an issue (`Closes #N`), pass CI (lint, type-check,
  tests, security scans) and use the PR template.
- Open an issue before a large PR; small fixes can go straight to a PR.

## Development setup

```
docker compose up
```

Backend (FastAPI, Python 3.12, `backend/pyproject.toml`), from `backend/`:
`ruff check .`, `ruff format --check .`, `mypy src`, `bandit -r src`, `pytest`.

Frontend (Next.js App Router, `frontend/package.json`), from `frontend/`:
`npm run lint`, `npm run typecheck`, `npm run build`, `npm test`.

## Reporting security issues

See [`SECURITY.md`](SECURITY.md). Do not use public issues for vulnerabilities.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
