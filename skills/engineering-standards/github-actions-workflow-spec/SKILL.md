---
name: github-actions-workflow-spec
description: Engineering specification and standards for GitHub Actions CI/CD workflows, script modularization (.github/scripts/), Vault OIDC authentication, matrix safety, and script deduplication. Use when creating, refactoring, or auditing GitHub Actions workflows and automation scripts.
---

# GitHub Actions Workflow Specification & Engineering Standard

Standard operating specification for writing clean, maintainable, secure, and reproducible GitHub Actions workflows and shell scripts.

## 1. External Script Execution Rule (No Inline Scripts)

- **Rule**: Do **NOT** write multi-line shell, Python, or complex commands in the `run:` block of `.github/workflows/*.yaml` files.
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

| Action | Standard Version Tag |
|---|---|
| Repository Checkout | `actions/checkout@v4` |
| Setup Python | `actions/setup-python@v5` |
| Upload Artifact | `actions/upload-artifact@v4` |
| Download Artifact | `actions/download-artifact@v4` |
| Vault Secrets OIDC | `hashicorp/vault-action@v4` |
| Setup Terraform | `hashicorp/setup-terraform@v3` |

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

- `common_configure_ssh_key.sh`: Decodes and configures SSH deploy keys cleanly.
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

## 6. Development & Pull Request Workflow

1. Always create a topic branch (`fix/*`, `feature/*`, `bugfix/*`).
2. Test script syntax locally via `bash -n .github/scripts/*.sh`.
3. Commit and push the topic branch to `origin`.
4. Open a Pull Request targeting `main` using `gh pr create`. Direct pushes to `main` or `release/*` are prohibited.
