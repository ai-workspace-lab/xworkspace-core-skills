---
name: multi-environment-delivery-and-release
description: Generic guidelines and routing rules for multi-environment (SIT/UAT/Prod) delivery, branching strategies, Vault OIDC isolation, and emergency secret handling for repos that deploy through GitHub Actions + Vault. Covers hardening JWT role bound_claims (repository alone is not isolation — pin job_workflow_ref/environment, prefer string over glob, short batch tokens); the three-tier Vault KV path layout (common services shared read-only, base credentials per-env read-only, environment secrets per-env read-write with prod denied delete) with its classification test and CI-enforceable invariants; and banning workflow_dispatch Vault-token escape hatches. Adapt the workflow file names and Vault role names to the target repo before applying.
---

# Multi-Environment Delivery and Release Standard

A reusable template for repos that route deployments through GitHub Actions and authenticate
to Vault via OIDC. Replace the placeholder workflow/role names below with the target repo's
actual ones; keep the routing shape and secret-handling rules.

## 1. Environment Routing Rules

A single delivery workflow (e.g. `<delivery-workflow>.yaml`) should route traffic to specific environments based on Git events. Never hardcode environments outside of these bounds:
- **`pull_request`** -> routes to **`sit`** environment.
- **`main` or `release/*` push** -> routes to **`uat`** environment.
- **`vMAJOR.MINOR.PATCH` tag** -> routes to **`prod`** environment.

## 2. Vault Authentication & Secrets
- **DO NOT** store sensitive credentials in GitHub Actions Secrets.
- Authentication must use GitHub OIDC → Vault JWT.
- Environments are strictly isolated. Ensure you select the correct Vault role for the context, following a naming convention like `github-actions-<repo>-sit` / `-uat` / `-prod`.

### 2.1 Hardening the JWT role binding

A JWT role is only as strong as its `bound_claims`. **Binding on `repository` alone is not isolation** — it lets *any* branch, *any* workflow, and *any* contributor with push access mint that role's token. Bind on repository **plus** a trigger-scope claim:

```json
{
  "role_type": "jwt",
  "user_claim": "sub",
  "bound_audiences": ["vault"],
  "bound_claims_type": "string",
  "bound_claims": {
    "repository": "<org>/<repo>",
    "job_workflow_ref": "<org>/<repo>/.github/workflows/<delivery>.yaml@refs/heads/main",
    "environment": "prod"
  },
  "token_policies": ["github-actions-<repo>-prod"],
  "token_no_default_policy": true,
  "token_type": "batch",
  "token_ttl": "20m",
  "token_max_ttl": "20m"
}
```

- **`user_claim`**: use `sub` (stable, encodes repo + ref + workflow). Avoid `actor` — it keys the Vault identity to a human username rather than the workload.
- **`bound_claims_type`**: default to `string` (exact match). Use `glob` only where a wildcard is genuinely required — a `*` matches `/` too, so `refs/heads/release/*` is satisfiable by any branch a repo writer can create.
- **`job_workflow_ref`**: pin it. Without it, a newly added or modified workflow file in the same repo can assume the role.
- **Prefer the `environment` claim over `ref` for prod.** A `ref`-based binding inherits the strength of branch protection; a GitHub Environment with required reviewers gates the token behind an approval.
- **Token limits**: short `token_ttl` + `token_max_ttl` (a CI job needs minutes, not hours), `token_no_default_policy: true`, and `token_type: batch` for non-renewable CI tokens.

### 2.2 KV path layout: three tiers

Per-environment isolation is defeated if every role can read one shared path holding cloud API keys, Terraform state credentials, or a global SSH private key. **The loosest role defines the effective privilege of the whole system**: if the `sit` role is bindable from any branch and can read that path, anyone who can push a branch owns the infrastructure.

Split the KV tree by whether a secret has an *environment dimension* at all:

| Tier | Path | sit | uat | prod | Permission |
|---|---|---|---|---|---|
| **① Common services** | `kv/data/<shared>` (registry pull creds, etc.) | ✅ | ✅ | ✅ | **read only, never writable** |
| **② Base credentials** | `kv/data/<shared>/<env>` (cloud API key, TF state creds, SSH deploy key) | own only | own only | own only | **read only** |
| **③ Environment secrets** | `kv/data/<env>/*` | own only | own only | own only | read/write (**prod: no `delete`**) |

**Classification test** — ask in order, first yes wins:

1. Does it grant *infrastructure control* or *host login*? → **②**. This is the actual vehicle for escalation: a sit compromise must not yield prod's cloud account or host private key.
2. Does its value change per environment? → yes **③**, no **①**.
3. Otherwise **③**. **Default to isolated; sharing needs an argument** for why one copy across three environments is *correct* — not merely that there happens to be one copy today.

**Permissions:**
- Tiers ① and ② are **read-only for every role**. Pipelines *consume* credentials; they do not *rotate* them. A shared asset must not be writable by any single environment's pipeline.
- `prod` must not hold `delete` on `kv/data/<env>/*`, and especially not on `kv/metadata/<env>/*` — metadata delete permanently destroys every version of a secret.

**Why ① and ② can coexist under one prefix:** in KV v2, `kv/data/<shared>` and `kv/data/<shared>/<env>` are *separate secrets* — a path can be both a secret and a prefix. A policy path of `kv/data/<shared>` matches the root **exactly and does not match subpaths** (that needs `kv/data/<shared>/*`). So "shared root + only your own subpath" holds strictly.

**Enforce it, don't just document it.** These are assertions, not conventions — verify them in CI:

- no policy names another environment's `kv/data/<shared>/<other-env>`;
- **no policy uses the `kv/data/<shared>/*` wildcard** — that single glob collapses tier ② in one step, and it is the premise the whole layout rests on;
- tiers ① and ② carry no `create`/`update`/`delete`/`patch`/`sudo`;
- `prod` carries no `delete` on either `kv/data` or `kv/metadata`.

> **Path isolation is not credential isolation.** Copying one credential set into three per-environment paths isolates the *paths* while the *credentials* stay shared — a sit compromise still yields prod. The structure is a precondition; the security benefit only lands once each environment holds genuinely distinct keys. Say which of the two you have actually achieved.

### 2.3 No escape hatches, no drift

- **Never accept a Vault token as a `workflow_dispatch` input.** Dispatch inputs are stored unmasked in run metadata and bypass every binding above. A "fallback for when JWT breaks" is a standing credential-injection path — fix the JWT instead.
- **Verify the role the workflow requests actually exists and its binding matches the triggering ref.** A workflow that maps tag pushes to a role bound to `refs/heads/*` fails auth at best, and silently routes to the wrong environment at worst. Keep the routing table (§1), the `VAULT_ROLE` expression, and the role definitions reviewed together — they drift independently.

## 3. Branching Lifecycle
- Always use Pull Requests. **Do not push directly to `main` or `release/*`**.
- `feature/*` and `bugfix/*` MUST target `main`.
- `hotfix/*` MUST target `release/*`.
- Production deployments ONLY occur via annotated tags (`v*`).

## 4. Emergency Secret Leaks
If a secret is exposed in the repository:
1. **Revoke** immediately in Vault/Provider.
2. **Generate** a new credential.
3. Purge the Git history (e.g. using `git filter-repo`)—do not merely "delete" the file in a new commit.
