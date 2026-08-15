---
name: multi-environment-delivery-and-release
description: AI Workspace Infra multi-environment delivery, Vault OIDC, release and secret-isolation rules. Use when changing GitHub Actions environment routing, Vault roles/policies, CI secret reads, workflow_dispatch inputs, release tags, or deployment paths in platform-ops-toolkit and related delivery repositories. Covers exact workflow allowlists, KV tiers, transition-safe routing, and no token escape hatches.
---

# Multi-Environment Delivery and Release Standard

A reusable template for repos that route deployments through GitHub Actions and authenticate
to Vault via OIDC. Replace the placeholder workflow/role names below with the target repo's
actual ones; keep the routing shape and secret-handling rules.

For AI Workspace Infra, read [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md) first. Treat the checked-in workflow plus its external scripts as execution truth; reconcile conflicting README prose rather than routing a deployment from documentation alone.

## 1. Environment Routing Rules

A single delivery workflow (e.g. `<delivery-workflow>.yaml`) should route traffic to specific environments based on Git events. Never hardcode environments outside of these bounds:
- **`pull_request`** -> routes to **`sit`** environment.
- **`main` or `release/*` push** -> routes to **`uat`** environment.
- **`vMAJOR.MINOR.PATCH` tag** -> routes to **`prod`** environment.

For `platform-ops-toolkit/platform-ops.yaml`, preserve the mapped resource file,
workspace, backend key, domain base, and Vault role as one atomic profile. Changing
only one of them can make Terraform manage one host while Ansible deploys another.

### 1.1 Cross-repository snapshot and deployment boundary

An immutable cross-repository snapshot is a build/release candidate, not an
implicit deployment request. Keep these stages separate:

1. Resolve the requested source ref to a SHA in every participating repository.
2. Create immutable snapshot tags through the approved short-lived automation
   identity.
3. Trigger and verify repository-local builds using the exact tag and SHA.
4. Select a snapshot only after all required artifacts and manifests pass.
5. Pass the selected tag explicitly to the environment deployment workflow.

Never use `main`, `latest`, or a partially successful snapshot as a deployment
version. Failed retries retain their tags and use a new `-rN` suffix. The
snapshot summary must preserve the workflow URL, per-repository SHA/build
status, artifact evidence, and any retry reason.

### 1.2 Universal Zero-Production-Fallback Rule (零生产兜底原则)

- **Default 绝不包含生产端点与资源**：在所有源代码、编译/构建模板、配置管理脚本（Ansible defaults/vars）、容器编排清单（Docker Compose / Kubernetes / Helm）及服务默认配置文件中，绝对禁止将生产环境的域名、IP、数据库 DSN、密钥或服务端点作为兜底退回值（default/fallback）。
- **非生产环境强隔离（Non-Production Isolation）**：Dev、Test、SIT、UAT 等非生产环境在任何缺省或参数未传状态下，严禁静默退回并连通生产资源或生产依赖服务。
- **Safe Fallbacks or Fail-Fast**：当必填服务地址、端点或依赖凭证未显示提供时，配置解析引擎必须严格遵循以下三种安全模式之一：
  1. **Safe Local Fallback**：仅退回至完全隔离且无公网风险的本地 Mock / Loopback 地址（如 `http://127.0.0.1:<port>` 或 `http://localhost:<port>`）；
  2. **Dynamic Host/Environment Derivation**：根据当前运行环境上下文或请求 Host 头强类型派生同环境同级子域名/服务名；
  3. **Fail-Fast**：在应用启动阶段或配置加载初始化阶段立即抛出异常或断言失败，禁止隐式降级运行。

### 1.3 Build-Time Artifact vs. Runtime Resolution Precedence (构建期产物与运行期决议优先级)

- **构建产物环境无关性（Immutable Environment-Agnostic Artifacts）**：任何编译打包产物（包括 Docker 镜像、二进制包、前端静态编译Bundle）必须保持环境无关。禁止在镜像构建阶段将特定环境的真实 upstream 端点硬编码写死至打包产物中。
- **运行期配置决议优先（Runtime Precedence）**：应用服务在运行时解析依赖端点与参数时，运行期动态配置（如环境变量注入、外部挂载的动态配置文件、服务发现）必须具备最高优先级，强制覆盖构建期打入的静态默认退回值。

### 1.4 End-to-End Orchestration Parameter Propagation (声明式编排全链路透传)

- **编排层显式透传**：容器编排文件（Compose / K8s Manifests）必须显式声明关键依赖服务 URL 的环境变量映射，确保宿主机或配置中心注入的环境配置能无损传递至应用程序容器。
- **配置管理模板动态派生**：配置管理系统（Ansible / Helm）渲染环境配置文件或秘密文件时，依赖服务的地址必须由当前环境的核心域名/网络变量动态派生，禁止跨角色写死字面值。

### 1.5 Production ref allowlist and tag semantics

Production eligibility is a hard allowlist, not a naming convention. A production-capable
workflow MUST fail closed unless `github.ref` matches one of:

- `refs/tags/vMAJOR.MINOR.PATCH` (the immutable stable release tag); or
- `refs/heads/release/vMAJOR.MINOR` (the protected release line, only when an explicit
  production action and approval are also present).

`main`, feature/bugfix branches, pull-request refs, arbitrary dispatch refs, and all
`daily-build-*` / `uat-daily-build-*` snapshots are non-production inputs. A workflow may
use a release branch to validate or stage a release, but it MUST NOT infer production
promotion from a branch name alone.

Stable and daily artifacts MAY share one tagging script. The shared tagging script MUST require or
derive an explicit tag kind and validate the complete tag/ref/environment matrix before
creating anything:

| Tag kind | Example | Allowed use |
|---|---|---|
| Stable | `v1.2.3` | Production promotion only after release gates |
| Daily/UAT | `uat-daily-build-YYYY.MM.DD-rN` | UAT/SIT validation and deployment only |
| Daily snapshot | `daily-build-YYYY.MM.DD-rN` | Non-production integration only |

Published stable tags MUST never be moved, overwritten, force-updated, or deleted. A failed
stable release gets a new version; a failed daily attempt gets a new `-rN` snapshot suffix.
The preflight MUST verify the event, ref, source SHA, tag immutability, artifact matrix,
artifact digest/provenance, GitOps desired version, Vault role/KV path, target route, and
required test conclusions before any production credential is read or deployment mutation
starts.

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
- **Allowlist new Vault workflows deliberately.** `platform-ops-toolkit` manages roles through `docs/tasks/vault_auth_split.sh`. Adding a workflow that calls Vault requires adding that exact workflow filename to `job_workflow_ref`, merging the configuration change, and having an authorized operator apply it. Do not widen the claim to an unrestricted wildcard.
- **Do not make an optional secret mandatory.** A DNS token belongs in a DNS-cutover-only Vault read. A resize or health-check path that does not switch DNS must not fail because Cloudflare credentials are absent.

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

## 5. Documentation cites Vault KV path + key name, never the value

A real incident: an account database export, an SMTP password, and an OAuth token manual all
ended up committed as literal values in markdown/YAML — live MFA TOTP secrets included — sitting
in a public repository's history for months before a `gitleaks` gate caught them. Regenerating
credentials fixed the accounts; the git history purge is the part that doesn't fix itself and
needs `git filter-repo` (§4) plus a force-push everyone with a clone must re-pull.

- **Documentation, runbooks, and example configs cite `kv/<path>` `<KEY_NAME>` — never the
  secret's actual value.** A setup guide that shows a real SMTP password or a real API key is
  itself a leak, indistinguishable in git history from one that was never meant to be read.
  Write `password: "{{ vault kv/CICD SMTP_PASSWORD }}"` or the equivalent for the pipeline in
  question, not the string it resolves to.
- **This includes "just an example" or "sanitized" values that are actually real.** The account
  export above was checked in as ops documentation, not intentionally as a secret — that
  distinction doesn't survive a `git clone`.
- **Data exports containing secrets (account dumps, API responses, debug captures) do not belong
  in the repository at all**, sanitized or not — they belong in the artifact/backup path that
  already exists for that purpose (§4 of the IaC spec's Vault-push pattern), not in docs/.
- **`gitleaks` failing on a PR that didn't introduce the secret is not a false positive to
  suppress.** It scans full history; a red Sec QA Gate on an unrelated PR means a prior commit
  leaked something and the fix is the purge above, not an allowlist entry.

## 6.1 UAT release closeout and recovery

For a multi-repository UAT release, completion is a controlled sequence, not a
single workflow result:

1. Merge each participating repository through a PR targeting `main`. Confirm
   the merge commit and required checks; do not tag a feature branch or a local
   worktree that was not merged.
2. Create one immutable, cross-repository snapshot tag (for example,
   `uat-daily-build-YYYY.MM.DD-rN`) from the resolved `main` SHAs. A failed
   attempt keeps its tag; retry with the next suffix rather than moving it.
3. Verify the image/package build for every deployable repository by exact tag
   and commit SHA. A repository tag, a successful tag matrix, or a successful
   workflow dispatch is not by itself proof that the artifact exists.
4. Update the UAT GitOps desired state through a PR. Pull-only CD means the
   deployment workflow must never write image tags into GitOps; it may validate
   the requested tag against the committed `.env.<env>` or equivalent.
5. Wait for the pull-only CD/reconciliation and verify the rendered image tag,
   service health, and migration status on the exact UAT hosts. Do not use
   production domains, DNS records, credentials, or database endpoints as a
   fallback during UAT validation.
6. Validate data flow at each boundary. For a usage path, verify exporter
   collection, Vector fan-out, authenticated Billing ingest, shared PostgreSQL
   write, Accounts read, and Portal display separately. Validate Grafana's
   remote-write path separately; missing Grafana data must not be “fixed” by
   coupling it to billing.
7. Record the tag, PRs, merge SHAs, GitOps PR/commit, workflow URLs, target
   environment, DNS result, service status, schema/migration result, and
   checkpoint results in `docs/tasks/` or the consuming repository's equivalent.

If any checkpoint is unknown, pending, or only inferred from a downstream UI,
the release remains incomplete. Use the evidence table in
`ci-cd-workflow-spec` to classify the fault before changing code or data.

### 6.2 DNS and authenticated cross-node ingress

- DNS creation/update is a separately auditable operation. Verify authoritative
  and public resolver answers before relying on an HTTPS endpoint; an old local
  resolver answer is not evidence that DNS is wrong.
- Cross-node ingest endpoints MUST use the same environment-scoped service
  authentication contract as peer internal services, plus network restriction
  where appropriate. Keep the application Bearer check independent from the
  Caddy/ingress route so a permitted network source still cannot write without
  the token.
- UAT checks MUST use redacted requests and never print the token. Test both
  expected success and expected unauthorized/forbidden behavior, without
  weakening production ingress or modifying production Xray configuration.
