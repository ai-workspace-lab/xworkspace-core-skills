---
name: github-actions-workflow-spec
description: Standards for GitHub Actions CI/CD workflows — external-script modularization (.github/scripts/), pinned action versions, concurrency/matrix safety, least-privilege permissions, Vault OIDC wiring, and non-interactive Terraform/Ansible steps. Use when creating, refactoring, or auditing GitHub Actions workflows and their shell scripts.
---

# GitHub Actions Workflow Specification

GitHub-Actions-specific rules for clean, secure, reproducible workflows. For policy that spans tools, defer to the sibling standards rather than restating them here:

- Environment routing (SIT/UAT/Prod) & Vault OIDC role names → `multi-environment-delivery-and-release`
- No-inline-scripts / code purity for HCL & playbooks → `infrastructure-as-code-spec`, `config-as-code-spec`
- Branching, PR targets, and committed-secret response → `project-development-standard`

## 1. No inline scripts

Keep every `run:` block to a single call. Put any non-trivial shell/Python in an executable script under `.github/scripts/` (`chmod +x`), and validate with `bash -n .github/scripts/*.sh`.

```yaml
- name: Install dependencies
  run: ${{ github.workspace }}/.github/scripts/platform-ops_provision_install-render-deps.sh
```

Pass Vault secrets and other values into scripts as step `env:`, never inline in the command.

## 2. Pin action versions

Use official, verified major tags — never invented or unverified ones:

| Action | Tag |
|---|---|
| `actions/checkout` | `@v4` |
| `actions/setup-python` | `@v5` |
| `actions/upload-artifact` / `download-artifact` | `@v4` |
| `hashicorp/vault-action` | `@v4` |
| `hashicorp/setup-terraform` | `@v3` |

## 3. Shared scripts

Reuse cross-workflow logic via `common_*.sh` scripts under `.github/scripts/` (e.g. `common_terraform_init_backend.sh`, `common_run_ansible_playbook.sh`, `common_configure_ssh_key.sh`). Step scripts delegate rather than copy:

```bash
#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${DIR}/common_terraform_init_backend.sh"
```

## 4. Concurrency & matrix safety

- **Scope concurrency by workflow + environment** so environments never block each other:
  ```yaml
  concurrency:
    group: <workflow-name>-${{ github.event.inputs.vault_env_path || 'uat' }}
    cancel-in-progress: false
  ```
- **Default matrix outputs** to `[]` / `0` when their source file is missing or during `destroy`:
  ```bash
  if [ -f cmdb.json ]; then
    hosts="$(jq -c 'keys' cmdb.json)"; count="$(jq 'length' cmdb.json)"
  else
    hosts="[]"; count="0"
  fi
  ```
- **Guard matrix jobs** on non-empty *and* non-zero counts:
  ```yaml
  if: ${{ needs.provision.outputs.count != '' && needs.provision.outputs.count != '0' && github.event.inputs.terraform_action == 'apply' }}
  ```
- Set `fail-fast: false` on deployment matrices so one bad host doesn't cancel the rest.

## 5. Permissions & log hygiene

- Declare least-privilege permissions at the top level:
  ```yaml
  permissions:
    contents: read
    id-token: write   # OIDC → Vault
  ```
- Never `set -x` around secrets. Mask any secret parsed by hand: `echo "::add-mask::$SECRET"`.

## 6. Non-interactive tooling

CI steps must never block on a prompt:

- Terraform: `terraform init -input=false`, `terraform apply -auto-approve -input=false`
- Ansible: `ANSIBLE_HOST_KEY_CHECKING=False`, `-o IdentityFile=~/.ssh/id_deploy -o StrictHostKeyChecking=no`

Upload `cmdb.json` and `inventory.ini` via `upload-artifact@v4` for audit trails.

## 7. Workflow roles (reference architecture)

`platform-ops-toolkit/.github/workflows` splits responsibilities into five patterns:

| Pattern | Example | Role |
|---|---|---|
| Orchestrator | `iac-pipeline-multi-cloud-master.yaml` | Calls child workflows via `workflow_call` + `secrets: inherit` |
| Multi-stage delivery | `platform-ops.yaml` | Job graph (`provision → deploy_* → data_migration → switch_dns`); state passed via artifacts |
| Component matrix | `resources-matrix.yaml` | `strategy.matrix` over `fromJSON(inputs.components_json)` |
| PR quality gate | `validate-release-pr.yml` | `pull_request` + `checkout` `fetch-depth: 0` + `gitleaks` |
| Readiness checker | `check-iaas-ready.yaml` | `workflow_dispatch`; inspects prior run status via the Actions API |

## 8. Before opening a PR

Run `bash -n .github/scripts/*.sh` and confirm `gitleaks` passes. Branch names and PR targets follow `project-development-standard`.
