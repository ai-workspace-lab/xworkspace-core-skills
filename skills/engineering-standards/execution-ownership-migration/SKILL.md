---
name: execution-ownership-migration
description: Migrate delivery execution out of a control-plane repository without breaking callers. Use when moving GitHub Actions scripts or workflow phases among platform-ops-toolkit, playbooks, iac_modules, gitops, and observability, or when reviewing their ownership and deletion order.
---

# Execution ownership migration

Read the [repository map](../references/ai-workspace-infra-repository-map.md) and inspect the current caller graph before editing. Classify code by what it **does**, not by its present directory or workflow name. Existing mixed-purpose scripts may need to be split; moving a file unchanged is not proof of reusable ownership.

| Layer | Owns | Must not become |
| --- | --- | --- |
| `platform-ops-toolkit` | Workflow entrypoints, environment/ref selection, approval, dispatch, OIDC/Vault boundary, GitOps reader/validator, release evidence and ownership-contract checks; thin adapters indispensable to its current workflows | A second implementation of reusable provider, host, database or observability execution |
| `playbooks` | Parameterized host/service roles and reusable workflows, including backup, migration, restore, deployment and host-level acceptance | A second store of environment topology or one script copy per environment |
| `iac_modules` | Provider modules, IaC renderers and execution/state adapters, CMDB production | Hand-maintained environment/provider declarations or application configuration |
| `gitops` | Non-secret desired-state declarations, including provider/environment resource configuration and release references | Imperative scripts, credentials, generated HCL/CMDB/inventory |
| Observability owner | Domain-specific telemetry pipeline, collector, dashboard and observability service implementation | A reason to place domain execution in Toolkit; generic host configuration can still be a Playbooks role |

The repository name can differ; locate its actual checkout and follow its local instructions. A script under `observability/` is not automatically Observability-owned: database restore on a host is a Playbooks concern, while telemetry-specific behavior belongs to the Observability owner. Likewise, a `gcloud`/`terraform` resource operation belongs to IaC Modules; Toolkit may select and invoke it but should not duplicate it.

## Required cutover order

1. **Inventory the contract.** Find every workflow, wrapper, test, runbook and external caller, plus inputs, outputs, credentials, permissions, target selection and failure behavior. Record the legacy path and intended owner in an inventory or PR. Resolve ambiguous ownership before moving code.
2. **Add the owner implementation.** Create or extend a reusable Role/Workflow/provider executor, with explicit environment and target inputs, idempotence or safe retry semantics, and owner-local tests. Keep secrets runtime-only. Merge or otherwise make an immutable reviewed owner ref available before the consumer uses it.
3. **Switch Toolkit callers.** Pin the reviewed owner ref, pass the same target and release identity, preserve output/evidence contracts and failure gates, and update all callers and contract tests. If a workflow filename or Vault-using job changes, migrate the exact `job_workflow_ref` allowlist and required permissions before dispatch. A local adapter may remain only when it is a thin, current-workflow control-plane shim.
4. **Verify the new route.** Run owner tests and renderer/Ansible/workflow checks as applicable; check every caller, output, negative path and environment boundary. Use UAT or a non-mutating rehearsal when runtime behavior changes. A green PR or dispatch alone is not live acceptance; record the exact owner SHA, Toolkit SHA, environment and evidence.
5. **Delete the old copy last.** Only after the new caller route is verified, remove the legacy executor and obsolete tests, update ownership inventory/docs, and search for stale references. If verification fails, retain the old copy and restore the previous pinned caller ref; do not silently fall back or report completion.

Keep separate PRs and validation evidence per owning repository. The dependency chain is owner implementation → Toolkit caller cutover → verified execution → legacy deletion. A single Toolkit PR may combine caller cutover and deletion only when owner code is already available and the replacement is independently tested. Never delete a called script merely to reduce the file count. Do not run a mutating environment workflow solely to validate a documentation or ownership refactor.

For stateful data operations, retain the release-specific backup, restore-test, checksum, schema-version and rollback gates from [CI/CD workflow standards](../ci-cd-workflow-spec/SKILL.md); this skill governs ownership and cutover, not permission to migrate or restore a database.
