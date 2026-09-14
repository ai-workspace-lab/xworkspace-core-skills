---
name: secrets-identity-and-access-governance
description: Govern Vault policies and roles, OIDC workload identity, least privilege, secret ownership, rotation, audit, emergency revocation, and environment isolation. Use when creating or changing access, onboarding a pipeline or service, rotating credentials, reviewing permissions, or responding to a suspected secret exposure.
---

# Secrets, Identity, and Access Governance

Treat identity policy as production code. Authentication, authorization, secret paths, and audit evidence must be reviewable, environment-scoped, and revocable.

## 1. Identity model

- Prefer workload identity: GitHub Actions or GitLab CI OIDC → Vault → short-lived provider/service credential.
- Bind roles to immutable, narrow claims: repository/project identity, approved workflow/pipeline path, protected ref/tag, environment, audience, and expiry. Do not use wildcards where a specific workflow or environment can be bound.
- Separate human, CI, service, break-glass, and provider identities. Do not reuse a root token or a shared admin identity for routine deployment.
- Keep environment paths and roles isolated. Derive the selected Vault path from a single approved runtime variable; do not scatter environment path literals or cross-environment fallback.

## 2. Secret lifecycle

For every secret record an owner, consumer, source, scope, rotation interval, last rotation, revocation method, dependency impact, and audit location. Prefer dynamic credentials; when static credentials are unavoidable, rotate them automatically or on a tested schedule.

Policies grant only the exact path/action needed. Separate read, write, administration, and recovery permissions. A pipeline that only reads deployment credentials must not list, write, or delete adjacent paths.

### 2.1 Vault KV v2 path contract

Use an environment-first path layout so a CI identity can be restricted by a
single prefix and a reviewer can identify the blast radius from the path alone:

```text
kv/<env>/platform/{oidc,jwt,cloudflare,gcp,observability,gitea}
kv/<env>/services/{xconnect,ai-workspace}
```

- `<env>` is an explicit, allowlisted value such as `uat` or `prod`; a missing
  value is a preflight error. Do not create a `kv/shared` credential bucket or
  copy one environment's provider key into another path.
- GitHub Actions authenticates with OIDC and receives read access only to the
  paths required by its environment and job. Terraform provisions projects,
  service accounts and workload identity bindings but never writes secret
  values to Git; Ansible writes or renders runtime configuration through Vault.
- A new secret path requires an owner, consumer, rotation interval, policy rule,
  and redacted verification record. CI checks must reject cross-environment
  path references, wildcard reads broader than the job allowlist, and any
  secret value in YAML, Terraform variables, artifacts or logs.

## 3. Change and audit

Treat policy/role changes as a two-part delivery: configuration change plus an authorization test from the intended workload identity. Verify the allowed path works, adjacent paths fail, the wrong environment/ref/workflow fails, and audit logs contain the expected actor, role, path, and request ID.

Never log, commit, artifact, cache, or persist secret values. Redact diagnostics while retaining safe identifiers such as role name, path (when non-sensitive), request ID, and status code.

### 3.1 Release-route and Vault consistency

For every delivery path, compute the environment once and use that same value for
the deployment route, GitHub Environment, Vault role suffix, KV path, artifact
selection, and release tests. Review the complete tuple together:

```text
event/ref -> environment -> artifact/tag -> route -> Vault role/KV path -> tests
```

Production credentials MUST be unreachable from `main`, pull-request refs,
feature/bugfix branches, and `daily-build-*` / `uat-daily-build-*` tags. A
production-capable path MUST be limited to `refs/tags/v*` or
`refs/heads/release/v*`, with protected-ref and approval checks enforced by the
workload identity. Test both the intended success path and the wrong-ref,
wrong-environment, and adjacent-secret denial paths; a successful Vault login
alone is not evidence that routing is correct.

## 4. Exposure and emergency access

On suspected exposure, contain first: revoke or disable the credential, identify consumers, rotate replacement values, validate recovery, then purge history when a value entered Git. A new commit deleting the value is insufficient.

Break-glass access must be separately owned, time-limited, fully audited, and tested. Its use opens an incident and requires post-use credential rotation and review.
