---
name: project-development-standard
description: Generic branching, PR, release, tagging, and secret-incident standard for a repo that ships from `main` plus `release/*` maintenance lines. Use whenever creating a branch, opening or reviewing a pull request, choosing a PR target (main vs release/*), backporting or cherry-picking a fix, cutting a release, creating a version tag, or responding to a committed secret. Adapt the branch-name prefixes and CI gate names to the target repo's actual conventions before applying.
---

# Project Development Standard

A reusable operational digest for teams running trunk-based development (`main`) alongside
`release/*` maintenance lines. Treat this as a template: keep the golden rules and direction
matrix, but replace the CI gate names and any repo-specific paths with the target repo's own.

## Golden rules

1. Never push directly to `main` or any `release/*` branch — every change lands through a PR, including docs-only changes and locally stranded commits.
2. Branch kind determines the PR target. Never mix directions.
3. Published tags are immutable. Never force-update, delete, or reuse one.
4. If a secret was committed: revoke it FIRST, rewrite history second (see below).

## Branch kinds and PR targets

| Branch | Purpose | PR target |
|---|---|---|
| `feature/*` | New feature work | `main` |
| `bugfix/*` | Normal bug fix for trunk | `main` |
| `hotfix/*` | Urgent fix for a published release line | `release/*` |
| `backport/*` | Fix moving from `main` to a release line | `release/*` |
| `cherry-pick/*` | Fix moving from a release line back to `main` | `main` |

Disallowed: `release/*`→`main`, `main`→`release/*` wholesale merges, `feature/*`→`release/*`, `hotfix/*`→`main`, `backport/*`→`main`, `cherry-pick/*`→`release/*`.

Before opening a PR, verify: source branch prefix matches the target branch per the table above. If the repo has a branch-direction CI gate, let it enforce this rather than reviewing it by hand.

## Opening a PR — required content

Every PR body must include:

- what user or engineering outcome the change delivers (one concise paragraph);
- links to the issue / task / original PR when one exists;
- the verification performed — name the exact test commands and results, and call out any intentionally unrun checks with the reason;
- migration, configuration, security, or rollback notes when the change can affect existing users or deployments.

Additionally for maintenance PRs:

- `hotfix/*` / `backport/*`: name the target `release/*` branch explicitly.
- `backport/*` / `cherry-pick/*`: link the original change, preserve the original commit SHA in the description, and state why the cross-branch transfer is required.

Public-repo hygiene: if the repository is public, PR bodies, commit messages, and committed docs must not contain credentials, tokens, internal hostnames, deploy targets, secret-store paths, or other internal infrastructure details.

## Merge policy

- Squash-merge `feature/*` and `bugfix/*` PRs — one reviewable commit per logical change on `main`.
- Keep `hotfix/*`, `backport/*`, `cherry-pick/*` small and traceable.
- Update a PR by rebasing its source branch; do not merge the base branch into a release-maintenance branch just to make it mergeable.
- Merge only after required reviews and required checks pass. Revert regressions with a new PR, never by force-pushing shared history.

## Releases and tags

- Cut `release/vMAJOR.MINOR` from a reviewed, stable `main` commit; after the cut it accepts only `hotfix/*` and intentional `backport/*`.
- Tags are SemVer `vMAJOR.MINOR.PATCH` (pre-releases: `-alpha.N` / `-beta.N` / `-rc.N`), annotated, created deliberately at a release point — never as a side effect of branch synchronization.
- Every published artifact must trace to exactly one release tag; each release records version, date, changelog, and any breaking/migration/security notes.

## Backport vs cherry-pick (direction cheat)

- Fix born on `main`, needed on a release line → `backport/*` → PR into `release/*`.
- Fix born on `release/*`, needed on trunk → `cherry-pick/*` → PR into `main`.
- One fix (or one tightly related fix set) per branch.

## Committed secret — emergency flow

1. Revoke the leaked credential immediately (before anything else).
2. Generate/rotate the replacement.
3. Review access logs for suspicious use.
4. Only after the credential is dead: rewrite history (`git filter-repo --path <file> --invert-paths`), then force-push branches and tags.
5. Tell collaborators to `git fetch --all` and re-align local branches.

A secret-scanning CI gate prevents new leaks but never replaces this flow for an already-exposed secret.

## CI gates to expect on PRs

Every repo names its own gates; treat this as the shape to fill in, not literal workflow names:

| Gate | Typical purpose |
|---|---|
| Branch direction | Rejects PRs whose source-branch prefix doesn't match the allowed target per the table above |
| Layered tests | Static analysis + unit/widget/golden tests on PRs into `main` |
| Build verification | Confirms the change actually builds/packages |
| Release E2E | End-to-end checks, often scheduled/dispatched rather than blocking every PR |

Changes touching packaging, permissions, authentication, secrets, or release scripts should get the repo's targeted security tests in addition to the normal PR checks — check the repo's own security docs for the current list.
