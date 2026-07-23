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

## 3. Change and audit

Treat policy/role changes as a two-part delivery: configuration change plus an authorization test from the intended workload identity. Verify the allowed path works, adjacent paths fail, the wrong environment/ref/workflow fails, and audit logs contain the expected actor, role, path, and request ID.

Never log, commit, artifact, cache, or persist secret values. Redact diagnostics while retaining safe identifiers such as role name, path (when non-sensitive), request ID, and status code.

## 4. Exposure and emergency access

On suspected exposure, contain first: revoke or disable the credential, identify consumers, rotate replacement values, validate recovery, then purge history when a value entered Git. A new commit deleting the value is insufficient.

Break-glass access must be separately owned, time-limited, fully audited, and tested. Its use opens an incident and requires post-use credential rotation and review.
