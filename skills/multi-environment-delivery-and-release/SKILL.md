---
name: multi-environment-delivery-and-release
description: Generic guidelines and routing rules for multi-environment (SIT/UAT/Prod) delivery, branching strategies, Vault OIDC isolation, and emergency secret handling for repos that deploy through GitHub Actions + Vault. Adapt the workflow file names and Vault role names to the target repo before applying.
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
