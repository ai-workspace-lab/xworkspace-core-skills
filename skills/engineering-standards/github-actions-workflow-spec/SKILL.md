---
name: github-actions-workflow-spec
description: Generic standards for GitHub Actions CI/CD workflows — external-script modularization (.github/scripts/), pinned action versions, concurrency/matrix safety, least-privilege permissions, Vault OIDC wiring, non-interactive Terraform/Ansible steps, and no-op/false-green deploy guards (a step that deployed nothing must fail red, not report success). Use when creating, refactoring, or auditing GitHub Actions workflows and their shell scripts. Treat the example workflow, script, job, and role names as a template to rename for the target repo.
---

# GitHub Actions Workflow Specification

GitHub-Actions-specific rules for clean, secure, reproducible workflows. **This is a generic template**: keep the rules, but treat every file, script, job, and role name below as an example to rename for the target repo. For policy that spans tools, defer to the sibling standards rather than restating them here:

- Environment routing (SIT/UAT/Prod) & Vault OIDC role names → `multi-environment-delivery-and-release`
- No-inline-scripts / code purity for HCL & playbooks → `infrastructure-as-code-spec`, `config-as-code-spec`
- Branching, PR targets, and committed-secret response → `project-development-standard`

## 1. No inline scripts

Keep every `run:` block to a single call. Put any non-trivial shell/Python in an executable script under `.github/scripts/` (`chmod +x`), and validate with `bash -n .github/scripts/*.sh`.

```yaml
- name: Install dependencies
  run: ${{ github.workspace }}/.github/scripts/<workflow>_<step>_install-deps.sh
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

## 7. Workflow roles

A multi-cloud IaC repo typically splits responsibilities across these five patterns. The file names are examples — rename to match your repo:

| Pattern | Example file | Role |
|---|---|---|
| Orchestrator | `pipeline-master.yaml` | Calls child workflows via `workflow_call` + `secrets: inherit` |
| Multi-stage delivery | `deploy.yaml` | Job graph (`provision → deploy_* → migrate → switch_dns`); state passed via artifacts |
| Component matrix | `resources-matrix.yaml` | `strategy.matrix` over `fromJSON(inputs.components_json)` |
| PR quality gate | `validate-pr.yaml` | `pull_request` + `checkout` `fetch-depth: 0` + secret scan (e.g. `gitleaks`) |
| Readiness checker | `check-ready.yaml` | `workflow_dispatch`; inspects prior run status via the Actions API |

## 8. Deploys must fail on no-op (no false green)

A green check must mean the remote state actually changed. The most dangerous CI defect is the **false green**: a "deploy" step exits `0` having done nothing, so a broken environment ships behind a wall of ✓s. Design every mutating step so that *doing nothing is an error*.

- **Ansible matches zero hosts → exit 0.** Both `ansible` (ad-hoc) and `ansible-playbook --limit` print `No hosts matched` / `provided hosts list is empty` and still succeed. A wrong inventory path or a mistyped host name then makes the whole deploy a silent no-op. Assert reachability *before* the mutating calls, via a shared guard:
  ```bash
  # common_assert_ansible_host.sh <inventory> <host> — fails red on missing
  # inventory file, no host match, or unreachable host.
  ping_out="$(ansible -i "${inventory}" "${host}" -m ping 2>&1 || true)"
  echo "${ping_out}"
  grep -q 'SUCCESS' <<<"${ping_out}" \
    || { echo "::error::'${host}' matched no reachable host in ${inventory}"; exit 1; }
  ```
- **Artifact paths are relative to the repo root, but the step's cwd may not be.** `download-artifact` with `path: cmdb` lands at `<repo-root>/cmdb`; a step with `working-directory: playbooks` must reach it as `../cmdb/inventory.ini`, not `cmdb/inventory.ini`. Pick one convention per job and apply it to *every* script the job calls — a single stale path silently degrades to the no-op above. When cwd is ambiguous, prefer `${GITHUB_WORKSPACE}/…` absolute paths.
- **`set -e` is not enough.** Use `set -euo pipefail` so unset secrets and broken pipes also fail. `set -e` will not catch a tool that itself exits 0 on an empty target — that is exactly what the reachability guard is for.
- **Verify the effect, not just the exit code.** A step that claims to change remote state should confirm it did — host matched, container `Up`, file present, migration row written — rather than trusting a `0`. Prefer `ansible-playbook` (task-level `changed`/`failed` accounting) over ad-hoc `ansible -m command` for anything non-trivial.
- **Guard the matrix, then guard inside.** `[]`/`0` matrix defaults (§4) stop a job from *running* on an empty fleet; the reachability assert stops a job that *did* run from *lying* when its target resolved to nothing. You need both.

## 9. Before opening a PR

Run `bash -n .github/scripts/*.sh` and confirm `gitleaks` passes. Branch names and PR targets follow `project-development-standard`.
