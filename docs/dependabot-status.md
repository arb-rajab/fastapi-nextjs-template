# Dependabot status

_Last updated: 2026-10-10. Starter template extracted from `lexicon`; update when the state changes._

## Configuration

- Ecosystems covered: pip (`/backend`), npm (`/frontend`), docker (`/backend`, `/frontend`), docker-compose (`/`), github-actions (`/`).
- Grouping: minor and patch updates grouped as `minor-and-patch` in every ecosystem.
- Schedule: weekly.
- Ignore rules: `typescript`, `eslint`, `eslint-config-next`, `next` and `@types/node` majors in `/frontend`; docker-compose image majors.

## State at last update

- Open Dependabot PRs: 0 (each merged or closed only after reading its checks).
- Default-branch CI: green at last check.
- Repository settings (read live 2026-10-10): public, `is_template` true, description set, default branch `main` (the only branch kept), secret scanning, push protection and Dependabot security updates enabled, dependency graph on (SBOM endpoint 200). Non-provider secret patterns and validity checks stay off: GitHub does not offer them on this user-owned public repo.
- Open in the 2026-10-10 loop (set by the repo owner through the API; the session's proxy blocks repository-settings writes): private vulnerability reporting (read: disabled), repository topics (none), `delete_branch_on_merge` (off). Alert state (Dependabot, code scanning, secret scanning) and fork-PR approval are read with the owner's token; see Notes once recorded.

## Time-limited exemptions

- `osv-scanner.toml`, every entry expiring 2026-11-09 (earlier than the source repos' 2026-11-15): `braces` GHSA-vfj7-8cjw-p6xm (dev tooling, never shipped). After that date the scan fails until each entry is renewed or removed. The scan is not a required check, so merges still work, but re-check each advisory for a fix before then.

## Notes

- Merge policy (deliberate choice by the repo owner, the same blanket policy as the application repos): every PR, major-version dependency bumps included, is squash-merged as soon as all of its required checks are green, confirmed per PR. This repo is a code showcase with no business or sensitive dependency, so green checks are the only gate. Red, pending or conflicted PRs are fixed or closed instead.
- `main` protection (2026-10-10, read back): pull request required (0 approvals), enforced for admins, force pushes and deletions blocked, "require branches to be up to date" off (`strict` false) on purpose. Nobody pushes to `main` directly; status-log updates go through a PR too.
- Required contexts: `Backend (lint, type-check, security, tests)`, `Frontend (lint, type-check, build, tests)`, `Secret scanning (gitleaks)`. Nothing else is required on purpose: osv-scanner, npm audit, dependency review and CodeQL depend on a moving advisory database or run only on some events.
- Closed unmerged on 2026-10-10, each with an explanatory comment: #2 (`node` 22 -> 25 in `/frontend`, non-LTS). If Dependabot recreates one, apply the merge policy; the closure is not re-raised. Dependabot does not re-propose a major after its PR is closed, so a later upgrade is a manual change.

## Deferred (not re-raised each pass)

- Alert reads (Dependabot, code scanning, secret scanning) and Actions settings (fork-PR approval) are blocked for Claude sessions by the proxy; they are read and written with the repo owner's token on their own machine.
- The owner keeps the token's Administration, Contents and Secret scanning permissions and does not rotate it (deliberate, 2026-10-09, reconfirmed 2026-10-10 for the template repos).
- Re-check the exemptions above before 2026-11-09 and drop each once its upstream fix ships.
