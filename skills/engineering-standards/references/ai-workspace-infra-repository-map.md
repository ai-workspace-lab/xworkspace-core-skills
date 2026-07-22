# AI Workspace Infra Repository Map

Read this reference before changing a repository under
`/Users/shenlan/workspaces/ai-workspace-infra`. The directory is a workspace of
independent repositories, not one monorepo. Discover the target's own
`AGENTS.md`, README, workflow, and current worktree state before editing.

## Authority and boundaries

| Target | Owns | Do not put here | Minimum focused verification |
| --- | --- | --- | --- |
| `artifacts` | OCI images, Helm/OCI charts, offline packages, Packer assets | Live topology, Vault policies, host configuration | Build/lint only the touched Dockerfile, chart, or package; check workflow path filters cover every input. |
| `docs` | Architecture and product/operations narrative | Executable deployment configuration | This directory is **not a Git worktree**. Preserve links and Markdown rendering; do not claim a PR/CI result for it. |
| `gitops` | Kustomize/Flux declarations and non-sensitive desired state | Secrets, generated inventories, playbooks, imperative scripts, application charts | `kustomize build` for each touched base/overlay. |
| `iac_modules` | Reusable Terraform modules, renderers, provider abstractions, generated CMDB contract | Credentials, hand-maintained inventory, service deployment | Apply `terraform-hcl-standard/AGENTS.md`; run `terraform fmt`/`validate` and renderer/inventory checks where available. |
| `observability.svc.plus` | Pigsty/Ansible-based observability stack, compose/templates, monitoring roles | General platform topology or unrelated app charts | Syntax-check touched playbooks/roles; treat DNS and ACME readiness as a deployment precondition. |
| `platform-ops-toolkit` | Control-plane workflows, Vault OIDC integration, Terraform orchestration, CMDB-driven Ansible deployment and migration | Provider module implementation, persistent secrets, hand-written host inventory | Validate touched scripts and workflow YAML; use the workflow's current job graph as runtime truth. |

## Cross-repository contracts

1. **Artifact flow:** `artifacts` publishes build outputs; `gitops` selects desired
   Kubernetes state; `platform-ops-toolkit` orchestrates infrastructure and host
   delivery; `iac_modules` provisions resources and produces CMDB facts;
   `observability.svc.plus` configures the observability stack. Do not move a
   concern across these boundaries just to make one PR convenient.
2. **Topology and inventory:** `cmdb.json` and `inventory.ini` are derived build
   artifacts. Terraform runtime facts plus static topology produce them; Ansible
   consumes them. Never commit a generated inventory or replace it with a host/IP
   literal.
3. **Topology migration is incomplete:** `gitops` documents
   `resources/<project>/<env>/<provider>/` as the declaration home, but the
   current `platform-ops.yaml` still renders Vultr host declarations from
   `iac_modules/terraform-hcl-standard/vultr-vps/config/resources/<env>/*.yaml`.
   Treat the executing workflow and renderer as authoritative. Do not duplicate
   or relocate declarations until the consumer is changed in the same reviewed
   migration.
4. **Workflow code wins over prose:** README pages can describe an earlier route
   or blast radius. Before changing a delivery path, inspect its workflow,
   external scripts, and actual job conditions; update drifted docs in the same
   change when practical.
5. **Secrets:** New or changed delivery paths use GitHub OIDC to Vault. Never
   introduce a GitHub Actions secret, a workflow-dispatch token input, a committed
   credential, or a plaintext generated secret. Adding a Vault-using workflow
   also requires the managed Vault role's exact `job_workflow_ref` allowlist to
   be updated through its configuration-as-code source and applied by an
   authorized operator.
6. **Destructive operations:** Enumerate exact provider resources first; require
   explicit confirmation for deletion, DNS cutover, source-instance destruction,
   state removal, or snapshot cleanup. Preserve a rollback point unless the user
   explicitly asks to remove it.

## Repository-specific operating notes

- `artifacts` contains older workflows that may use inline shell or repository
  secrets. Do not copy those patterns into new delivery workflows. Make focused
  changes; a security migration is a separate scoped task.
- `gitops` uses Kustomize bases and environment overlays. Keep generated names
  stable unless a deliberate rollout requires a new identity; do not add secrets
  to ConfigMaps or values files.
- `iac_modules/terraform-hcl-standard/**` has a binding `AGENTS.md`: loops are
  rendered in Python/Jinja2, not in environment HCL; YAML plus runtime Terraform
  outputs form the CMDB contract.
- `observability.svc.plus` combines Ansible, Pigsty-like entry playbooks, Docker
  Compose, Terraform, and shell installers. Change only the layer that owns the
  requested behavior. For public HTTPS changes, verify the DNS record exists
  before relying on Caddy/ACME.
- `platform-ops-toolkit` has both reusable multi-cloud pipelines and a business
  domain delivery path. The latter is currently Vultr-only; reject other
  providers before fetching credentials or applying Terraform. Its normal flow
  is render → Terraform → CMDB/inventory → Ansible → optional migration/DNS.

## Shared inspection checklist

```bash
git -C <repo> status --short --branch
rg --files -g 'AGENTS.md' -g 'README*.md' -g 'CONTRIBUTING.md' <repo>
rg -n 'workflow_dispatch|workflow_call|permissions:|concurrency:|vault-action' <repo>/.github
```

Keep unrelated dirty files untouched. Do not reset, checkout, stage, or delete
them merely to make the target change easier.

Preserve the local dialect: retain adjacent YAML indentation and action-pinning
style, shell safety/header conventions, Terraform layout, and Markdown voice.
Format only the touched language or files; never run a repository-wide rewrite
as incidental cleanup.
