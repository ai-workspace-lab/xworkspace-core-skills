---
name: execution-ownership-migration
description: Enforce the four-repository execution boundary and safe cutover among platform-ops-toolkit, gitops, iac_modules, and playbooks. Use for new workflows, scripts, roles, provider changes, migration work, or moving execution logic.
---

# 四边界执行归属规范（强制）

先读取[仓库地图](../references/ai-workspace-infra-repository-map.md)，并检查当前 caller graph。判定代码归属必须按实际副作用，而不是按目录名、workflow 名称或“bootstrap/validator/diagnostic”命名。已有混合脚本可能需要拆分；原样移动文件不等于形成可复用 owner。

这份 skill 是四个基础设施仓库的共同判定源。每个受管仓库根目录的 `AGENTS.md` 必须引用它；如果 skill 未被当前 Agent 加载，根 `AGENTS.md` 仍然有效，不能以“没有加载 skill”为例外。

## 1. 四边界判定表

按以下顺序询问，第一项为“是”即确定 owner：

1. 是否创建、修改、查询或删除云资源、DNS、Registry、OS Login、临时防火墙、Terraform state，或产出云资源事实/CMDB？→ **IaC Modules**。
2. 是否通过 SSH、Ansible、Docker、systemd、包管理器、主机文件、Caddy/Xray，或 PostgreSQL/备份/恢复/服务健康检查操作主机和服务？→ **Playbooks Roles**。
3. 是否只是声明目标拓扑、资源参数、版本、域名、非敏感配置引用？→ **GitOps**。
4. 是否只做入口、审批、环境/目标选择、Vault/OIDC 授权、阶段编排、固定 SHA 派发、证据校验和最终放行？→ **Toolkit**。

| Boundary | Must own | Must not own |
| --- | --- | --- |
| `platform-ops-toolkit` | Workflow entrypoints, environment/ref selection, approval, Vault/OIDC boundary, fixed-SHA dispatch, evidence/checksum/digest validation, final promotion gate, GitOps reader/validator | SSH/Ansible/Docker/systemd/package/database/backup/restore/service execution; cloud/DNS/Registry/state mutation |
| `gitops` | Declarative topology, provider/environment resources, versions/tags/digests, domains, and non-secret configuration references | Executable scripts, provider API calls, host/service/database actions, runtime IPs, CMDB, secret values |
| `iac_modules` | Terraform/provider modules, cloud resources, DNS, Registry, OS Login, temporary firewall, state, and cloud facts/CMDB rendering | Host/service/database execution, certificates, health checks, migrations, backups/restores, business data |
| `playbooks` Roles | Parameterized host/service roles and reusable workflows, host baseline, Caddy/certificates, Xray/proxy, Observability, database migration/backup/restore, diagnostics and health checks | Cloud/DNS/Registry/OS Login/firewall/state mutation, authoritative CMDB generation, environment topology ownership |
| Observability owner | Domain-specific telemetry pipeline, collector, dashboard and service implementation | A reason to place host/service execution in Toolkit; generic host configuration remains a Playbooks role |

Playbooks may consume IaC-generated CMDB but must not generate or modify authoritative cloud facts. Toolkit may validate CMDB evidence but must not execute cloud or host actions. A change matching two rows must be split into an owner implementation and a thin caller.

## 2. Standard data flow

```text
GitOps declaration
  → Toolkit selection/approval/authorization/fixed version
  → IaC Modules cloud action and CMDB output
  → Toolkit CMDB/evidence check
  → Playbooks Roles host/service/database action
  → Toolkit evidence aggregation and final gate
```

## 3. Required cutover order

1. **Inventory the contract.** Find every workflow, wrapper, test, runbook and external caller, plus inputs, outputs, credentials, permissions, target selection and failure behavior. Record the legacy path and intended owner in an inventory or PR. Resolve ambiguous ownership before moving code.
2. **Add the owner implementation.** Create or extend a reusable Role/Workflow/provider executor, with explicit environment and target inputs, idempotence or safe retry semantics, and owner-local tests. Keep secrets runtime-only. Merge or otherwise make an immutable reviewed owner ref available before the consumer uses it.
3. **Switch Toolkit callers.** Pin the reviewed owner ref, pass the same target and release identity, preserve output/evidence contracts and failure gates, and update all callers and contract tests. If a workflow filename or Vault-using job changes, migrate the exact `job_workflow_ref` allowlist and required permissions before dispatch. A local adapter may remain only when it is a thin, current-workflow control-plane shim.
4. **Verify the new route.** Run owner tests and renderer/Ansible/workflow checks as applicable; check every caller, output, negative path and environment boundary. Use UAT or a non-mutating rehearsal when runtime behavior changes. A green PR or dispatch receipt alone is not live acceptance; record the exact owner SHA, Toolkit SHA, environment and evidence.
5. **Delete the old copy last.** Only after the new caller route is verified, remove the legacy executor and obsolete tests, update ownership inventory/docs, and search for stale references. If verification fails, retain the old copy and restore the previous pinned caller ref; do not silently fall back or report completion.

The dependency chain is **owner implementation → Toolkit caller cutover → verified execution → legacy deletion**. Never delete a called script merely to reduce the file count. Do not run a mutating environment workflow solely to validate a documentation or ownership refactor.

## 4. Mandatory merge gates

- New files must declare `owner`, `caller`, side-effect resources, and input/output evidence in the PR description.
- A read-only schema/CMDB/manifest check does not automatically change ownership; inspect the command's final side effect.
- Toolkit legacy execution candidates remain frozen; migration must establish the owner implementation first. The Toolkit scanner is a guard, not owner approval or UAT evidence.
- Executable scripts/runtime CMDB in GitOps, host/database actions in IaC, provider/DNS/state actions in Playbooks, or execution commands in Toolkit are blocking violations.
- Cross-boundary work must provide four evidence sections: owner implementation, caller diff, verification result, and legacy-copy deletion result.
- Unclear ownership, stale callers, local-only verification, missing UAT evidence, or two executable implementations stop merge and release.

## 5. Agent loading contract

Each governed repository must have a root `AGENTS.md` linking this skill and restating its local allowlist/denylist. Agents must read it before editing. If the root file is missing, the skill link is broken, or the worktree contains unrelated unapproved changes, stop and report the boundary problem before implementation changes.

For stateful data operations, retain release-specific backup, restore-test, checksum, schema-version and rollback gates from [CI/CD workflow standards](../ci-cd-workflow-spec/SKILL.md); this skill governs ownership and cutover, not permission to migrate or restore a database.
