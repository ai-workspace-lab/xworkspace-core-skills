---
name: github-actions-workflow-spec
description: Engineering specification and standards for GitHub Actions CI/CD workflows, script modularization (.github/scripts/), Vault OIDC authentication, matrix safety, Ansible/Terraform pipeline integration, multi-workflow orchestration, and script deduplication. Use when creating, refactoring, or auditing GitHub Actions workflows and automation scripts.
---

# GitHub Actions Workflow Specification & Engineering Standard

Standard operating specification for writing clean, maintainable, secure, and reproducible GitHub Actions workflows and shell scripts.

## 1. External Script Execution Rule (No Inline Scripts)

- **Rule**: Do **NOT** write multi-line shell, Python, or complex inline commands in the `run:` block of `.github/workflows/*.yaml` files.
- **Requirement**: All non-trivial step execution logic must be placed in executable external scripts under `.github/scripts/`.
- **Workflow Invocation**: The workflow file should cleanly invoke the external script:
  ```yaml
  - name: Install dependencies
    run: ${{ github.workspace }}/.github/scripts/platform-ops_provision_install-render-deps.sh
  ```
- **Permissions**: Every script in `.github/scripts/` must be executable (`chmod +x`).
- **Validation**: All scripts must pass syntax checks via `bash -n .github/scripts/*.sh`.

## 2. Action Versioning Standards

Use official, verified major version tags. Never hardcode unverified or non-existent action versions:

| Action | Standard Version Tag | Purpose |
|---|---|---|
| Repository Checkout | `actions/checkout@v4` | Checkout git repo branches |
| Setup Python | `actions/setup-python@v5` | Python 3.12+ execution environment |
| Upload Artifact | `actions/upload-artifact@v4` | Store build & CMDB artifacts |
| Download Artifact | `actions/download-artifact@v4` | Fetch artifacts between matrix jobs |
| Vault Secrets OIDC | `hashicorp/vault-action@v4` | JWT OIDC authentication to HashiCorp Vault |
| Setup Terraform | `hashicorp/setup-terraform@v3` | Terraform CLI execution |

## 3. Environment Routing & Vault OIDC Isolation

### Multi-Environment Event Routing
Workflows must route to target environments based strictly on Git trigger events:
- **`pull_request`** -> **`sit`** environment
- **`push` (`main` / `release/*`)** -> **`uat`** environment
- **`push` (`vMAJOR.MINOR.PATCH` tag)** -> **`prod`** environment

### Vault Secrets Management
- **Never** store sensitive credentials in GitHub Actions Secrets.
- Authenticate via GitHub OIDC → Vault JWT using strictly isolated role names:
  ```yaml
  VAULT_ROLE: github-actions-<repo>-${{ github.event.inputs.vault_env_path || 'uat' }}
  ```
- Pass loaded Vault secrets as step environment variables to external scripts rather than embedding values into commands.

## 4. Script Deduplication & Modular Utilities

Common tasks across workflows must reuse shared utility scripts under `.github/scripts/` using the `common_*.sh` prefix:

- `common_configure_ssh_key.sh`: Decodes and configures SSH deploy keys cleanly (`~/.ssh/id_deploy`).
- `common_terraform_init_backend.sh`: Initializes Terraform S3 backends accepting dynamic `STATE_KEY`.
- `common_terraform_apply_destroy.sh`: Runs `terraform apply` or `destroy` depending on `TERRAFORM_ACTION`.
- `common_setup_matrix_terraform_cli_args.sh`: Configures multi-cloud Terraform matrix CLI arguments.
- `common_generate_resource.sh`: Wraps `python3 scripts/generate.py <cmd>` calls for resource rendering and CMDB generation.
- `common_run_ansible_playbook.sh`: Standardizes `ansible-playbook` invocation with inventory and SSH settings.

Specific step scripts should delegate directly to common utilities:
```bash
#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${DIR}/common_terraform_init_backend.sh"
```

## 5. Concurrency & Matrix Execution Safety

- **Concurrency Scoping**: Always scope `concurrency:` groups by workflow and target environment to prevent cross-environment locking:
  ```yaml
  concurrency:
    group: <workflow-name>-${{ github.event.inputs.vault_env_path || 'uat' }}
    cancel-in-progress: false
  ```
- **Safe Matrix Outputs**: Step outputs that build JSON matrix arrays (e.g. `hosts`) must provide safe default fallbacks (`[]` / `0`) when files (such as `cmdb.json`) are absent or during `destroy` actions:
  ```bash
  if [ -f cmdb.json ]; then
    hosts="$(jq -c 'keys' cmdb.json)"
    count="$(jq 'length' cmdb.json)"
  else
    hosts="[]"
    count="0"
  fi
  ```
- **Matrix Guard Conditions**: Job-level `if:` conditions consuming matrix count outputs must check for both non-empty and non-zero counts:
  ```yaml
  if: ${{ needs.provision.outputs.count != '' && needs.provision.outputs.count != '0' && github.event.inputs.terraform_action == 'apply' }}
  ```
- **Fail-Fast Configuration**: Set `fail-fast: false` on deployment matrices to allow other host deployments to complete even if one host encounters transient network issues.

## 6. Multi-Workflow Architecture & Pipeline Roles

Based on reference repository architecture (`platform-ops-toolkit/.github/workflows`), workflows are classified into 5 distinct operational patterns:

### 1. Master Pipeline Orchestrator (`iac-pipeline-multi-cloud-master.yaml`)
- Coordinates child pipelines sequentially or in parallel via `on: workflow_call` / `uses: ./.github/workflows/<sub-workflow>.yaml`.
- Passes input choices (`deploy_action`, `project`, `vault_env_path`, `cloud_provider`) down to child workflows with `secrets: inherit`.

### 2. Multi-Stage Site Recovery & Data Migration (`platform-ops.yaml`)
- Multi-stage job dependency graph (`provision` -> `deploy_base` -> `deploy_web_saas` -> `deploy_infra_platform` -> `deploy_agent_proxy` -> `data_migration` -> `switch_dns`).
- Transfers state between jobs using `upload-artifact@v4` / `download-artifact@v4`.

### 3. Component Matrix Pipelines (`iac-pipeline-multi-cloud-account-matrix.yaml`, `resources-matrix.yaml`)
- Evaluates dynamic component arrays (`components_json: '["vpc","role"]'`) via `strategy: matrix: component: ${{ fromJSON(inputs.components_json) }}`.
- Reuses common CLI argument generators (`common_setup_matrix_terraform_cli_args.sh`).

### 4. Security & PR Quality Gate (`validate-release-pr.yml`)
- Triggered on `pull_request` (`opened, synchronize, reopened`).
- Checks full commit history (`actions/checkout@v4` with `fetch-depth: 0`) and executes static secret detection (`gitleaks`).

### 5. Infrastructure Readiness Checker (`check-iaas-ready.yaml`)
- Lightweight status verifier triggered on `workflow_dispatch`.
- Inspects GitHub Actions API for previous workflow run outcomes before triggering downstream deployments.

## 7. Least-Privilege Permissions & Logging Safety

- **Minimal Workflow Permissions**: Declare exact required permissions at top level:
  ```yaml
  permissions:
    contents: read
    id-token: write
  ```
- **Log Hygiene & Secret Masking**:
  - Never run `set -x` in scripts processing sensitive credentials or Vault secrets.
  - Dynamically masked secrets must use `echo "::add-mask::$SECRET"` if manually parsed from API payloads.

## 8. Automated Tooling Standards (Terraform & Ansible)

- **Non-Interactive Execution**: Always pass non-interactive flags to infrastructure tooling:
  - Terraform: `terraform init -input=false`, `terraform apply -auto-approve -input=false`
  - Ansible: Pass `ANSIBLE_HOST_KEY_CHECKING=False` and explicit identity file `-o IdentityFile=~/.ssh/id_deploy -o StrictHostKeyChecking=no`.
- **Artifact Auditability**: Upload generated `cmdb.json` and `inventory.ini` as workflow artifacts (`actions/upload-artifact@v4`) for operational tracing.

## 9. Development & PR Security Gate Workflow

1. Always create a topic branch (`fix/*`, `feature/*`, `bugfix/*`).
2. Test script syntax locally via `bash -n .github/scripts/*.sh`.
3. Ensure security gates (`gitleaks` secret detection) pass cleanly.
4. Commit and push the topic branch to `origin`.
5. Open a Pull Request targeting `main` using `gh pr create`. Direct pushes to `main` or `release/*` are prohibited.
