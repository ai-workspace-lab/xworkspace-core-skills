---
name: project-development-standard
description: AI Workspace Infra branching, PR, release, tagging and incident standard. Use whenever changing one of its independent repositories, creating or reviewing a PR, choosing a target branch, handling dirty worktrees, coordinating a cross-repo change, cutting a release, or responding to a committed secret.
---

# Project Development Standard

A reusable operational digest for teams running trunk-based development (`main`) alongside
`release/*` maintenance lines. Treat this as a template: keep the golden rules and direction
matrix, but replace the CI gate names and any repo-specific paths with the target repo's own.

Read [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md) before creating a branch. `artifacts`, `gitops`, `playbooks`, `iac_modules`, `observability.svc.plus`, and `platform-ops-toolkit` are separate repositories; `docs` is a non-Git documentation tree. Never report one repository's check or PR as verification for another.

## Golden rules

1. Never push directly to `main` or any `release/*` branch — every change lands through a PR, including docs-only changes and locally stranded commits.
2. Branch kind determines the PR target. Never mix directions.
3. Published tags are immutable. Never force-update, delete, or reuse one.
4. If a secret was committed: revoke it FIRST, rewrite history second (see below).
5. Preserve unrelated local changes. Inspect `git status --short --branch` before switching branches or staging; only stage named target paths.

## Local `main` and worktree discipline

The local `main` checkout is an integration mirror, not a development workspace.
Use it only to fetch, fast-forward, inspect the merged result, and create an
isolated worktree. Do not edit files, run experimental deployment changes, or
accumulate uncommitted work on local `main`.

Before pulling or changing branches:

1. Run `git status --short --branch` and classify every tracked and untracked
   path. Never use `reset --hard`, `clean`, `checkout -- <path>`, or an
   unrecorded stash to make a dirty checkout pullable.
2. If local `main` is dirty, preserve the named work in a topic or recovery
   branch first. A recovery commit is acceptable when it is the safest way to
   preserve the exact local state; it is not automatically a merge candidate.
3. Compare the preserved snapshot with `origin/main` before opening a PR.
   Files already present with identical content on `origin/main` are not new
   work and must not be recommitted merely because an old local checkout showed
   them as untracked.
4. Update the integration mirror only after it is clean, using
   `git fetch origin main` and `git pull --ff-only`. A non-fast-forward result
   requires investigation, not a forced update.

Prefer one worktree per task:

```bash
git fetch origin main
git worktree add ../<repo>-<task> -b feature/<issue>-<task> origin/main
```

All edits, commits, tests, and PR work happen in that topic worktree. Keep the
local `main` worktree clean and short-lived. If an uncommitted change is found
on `main` after work has started, stop and perform the preservation/comparison
sequence above before doing anything else.

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

For a cross-repository change, open a focused PR in each affected repository. Link
the companion PRs and state the merge/order dependency, the compatibility window,
and the rollback owner. Do not merge a consumer before the module/declaration it
requires is available on the declared ref.

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

### Cross-repository snapshots

For a coordinated build across repositories:

- define the participating repository and artifact matrix before tagging;
- resolve and record the source SHA for every repository;
- use one immutable daily naming series: `uat-daily-build-YYYY.MM.DD-rN`;
- allocate `r1` for the first snapshot on a UTC date, then increment the same
  date's suffix (`r2` … `rN`) for every retry or later snapshot; reset to `r1`
  only when the UTC date changes;
- resolve the next suffix against all participating repositories before matrix
  fan-out, and never move, delete, or reuse an existing snapshot tag;
- verify the CI run matches both the tag and expected SHA, then verify the
  required image/package/chart/manifest before selecting the snapshot;
- keep tag creation, artifact builds, and environment deployment as separate
  auditable stages.

The handoff must state whether the snapshot is deployable, tag-ready only, or
blocked, and include per-repository evidence. A successful build in one
repository does not establish a successful cross-repository release.

### Release, consumer-pin, and deployment order

When a workflow consumes artifacts from another repository, use this order:

1. Merge the producer implementation through its PR and verify the merged
   commit.
2. Publish a new immutable release tag from that reviewed commit and verify
   the expected assets/checksums.
3. Update each consumer's GitOps/workflow release tag and source SHA in a
   separate focused PR. Do not dispatch deployment using stale pins.
4. Wait for the consumer PR checks, merge it, and record the resulting
   immutable refs.
5. Dispatch UAT with those exact refs; promote further only after the UAT
   acceptance evidence is complete.

If a preflight fails before resource mutation, fix the owning contract first.
Do not bypass the check by widening a Vault policy, accepting a mutable ref, or
reusing an old release. For cross-repository changes, record the dependency
order and rollback owner in each PR.

### Production ref and tag gate

The only refs eligible to enter a production-capable path are:

- `refs/tags/v*` for the immutable stable release artifact; or
- `refs/heads/release/v*` for a protected release line with an explicit,
  reviewed production action.

Everything else, including `main`, pull-request refs, feature/bugfix branches,
`daily-build-*`, and `uat-daily-build-*`, MUST be rejected by the production
entry gate. A shared tag script is acceptable only when it validates tag kind and
environment semantics; it must not treat a successful tag creation as proof that
the artifact is deployable.

Stable tags are append-only history. Do not move, overwrite, force-update, or
delete a published stable tag. Use a new SemVer tag for a stable retry and a new
`-rN` suffix for a daily snapshot retry.

Before release publication, record passing evidence for the source ref/SHA,
artifact build and digest, required tests, Vault role and KV path, environment
route, GitOps desired version, and deployment/rollback plan. If any item is
unknown or inferred only from a downstream UI, the release is blocked.

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
