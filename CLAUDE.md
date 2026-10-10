# CLAUDE.md

Notes for Claude Code sessions working in this repository. Each item below
saves a round trip; update the file when you learn something else.

## Layout

- `backend/`: FastAPI. Package `backend/src/starterapp/`. Errors always go
  through `api/errors.py` so every response keeps the `{"error": {...}}` shape.
- `frontend/`: Next.js App Router. The browser never calls the backend
  directly; `frontend/app/api/**` route handlers proxy to it with the session
  cookie turned into a bearer token. The backend has no CORS middleware on
  purpose.
- Only `.env.example` is committed. Never create or commit `.env`.

## Backend tests need real Postgres and Redis

`pytest` runs migrations and truncates tables, so it needs a live Postgres and
Redis (no SQLite, no mocks for grants or rate limits). Defaults expect
Postgres on `localhost:5433` and Redis on `localhost:6380`; override with
`DATABASE_ADMIN_URL`, `DATABASE_URL`, `REDIS_URL`. The test database user must
be able to create roles (migration 0002 creates the runtime role).

If a sandbox has no Docker daemon, install Postgres 16 and Redis from the OS
packages, create the admin role and database as the `postgres` OS user
(`su postgres -c "psql ..."`), never `-h 127.0.0.1 -U postgres`, which hangs on
a password prompt with no TTY.

Add every new table to `ALL_TABLES` in `backend/tests/conftest.py` and grant
it to the runtime role in its migration, or tests fail with a confusing
`permission denied for table`.

## Pagination

Order every paginated query by something unique (end with the primary key), or
rows repeat or vanish between pages. `PageParams` rejects bad values with a 422
rather than clamping; keep that so client bugs surface.

## Always `tail` tool output

`pip install`, `pytest`, `npm install` and `next build` are verbose; read the
end of the output.

## Frontend lint and versions

- Keep `eslint-config-next` on the same version as `next` (both are 16.x). It
  ships flat configs, so `eslint.config.mjs` needs no `FlatCompat`.
- eslint-config-next 16 enables the React Hooks v7 rules. Calling `setState`
  synchronously in an effect fails lint; follow the patterns in `lib/hooks.ts`
  and `lib/auth.tsx` (set state only after an `await`, with a cancel flag).
- Stay on TypeScript 5.9 and ESLint 9 until typescript-eslint and
  eslint-config-next support TypeScript 7 and ESLint 10. Dependabot ignores
  those majors on purpose.
- `@types/node` must match the Node version the Dockerfiles and CI use (22).
- `npm install` works without `--legacy-peer-deps`. `next build` rewrites
  `tsconfig.json` and `next-env.d.ts`; commit the result.

## Shared components

`components/ui/` holds the generic building blocks; build pages from them
rather than adding one-off markup. A field error comes from `ApiError.fields`
(or `AuthError.fields`) and goes into `FormField`'s `error` prop. Styles for
them are plain classes at the end of `app/globals.css`.

## Cookies and hostnames

Cookies are scoped by hostname, not port. Use `localhost` for both the
frontend and any manual API calls; mixing `localhost` and `127.0.0.1` breaks
the session cookie in a way that looks like an auth bug.

`COOKIE_SECURE` must stay `false` until the app is actually served over HTTPS,
because browsers silently drop a `Secure` cookie sent over plain HTTP.

## Docker in restricted sandboxes

Docker image pulls and `docker build` (which runs `pip install` and `npm ci`
inside the build) often fail in sandboxes with an egress proxy. Do not loop on
it; rely on CI's jobs for image verification. The Docker Hub CDN is the usual
blocked host.

## Security conventions

- `login` must always run `verify_password` (against a dummy hash for unknown
  users) so response time does not reveal which usernames exist.
- Rate limiters fail open on a Redis outage by design.
- Do not add real secrets anywhere. `JWT_SECRET_KEY` defaults are labelled
  dev-only placeholders.
- `osv-scanner.toml` entries must be dated and carry a reason. Do not widen
  `.gitleaksignore` or `osv-scanner.toml` without the owner's sign-off.
