---
name: github-actions-workflow-spec
description: GitHub Actions standards for AI Workspace Infra workflows and external scripts. Use when creating, refactoring, or auditing workflows in platform-ops-toolkit, artifacts, gitops, playbooks, iac_modules, observability.svc.plus, or their shell scripts. Covers CI/CD separation, external-script modularization, pinned actions, concurrency and matrix safety, least-privilege permissions, Vault OIDC, Terraform/Ansible safety, CMDB artifacts, false-green prevention, invocation-shape reuse, and eliminating hardcoded environment-varying values without blindly modernizing legacy workflows.
---

# GitHub Actions Workflow Specification

GitHub-Actions-specific rules for clean, secure, reproducible workflows. **This is a generic template**: keep the rules, but treat every file, script, job, and role name below as an example to rename for the target repo. For policy that spans tools, defer to the sibling standards rather than restating them here:

Read [AI Workspace Infra Repository Map](../references/ai-workspace-infra-repository-map.md) first. Apply the target repository's current workflow conventions; do not copy a legacy workflow's inline scripts, secrets, or broad trigger scope into a new delivery path.

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

Reuse the target repository's already-approved action version unless the task is an
explicit action-upgrade. Verify the exact tag or SHA against the action publisher;
never invent a version. New security-sensitive workflows should prefer immutable
full-SHA pins where that repository already uses them.

| Action | Tag |
|---|---|
| `actions/checkout` | target-repository approved version/SHA |
| `actions/setup-python` | target-repository approved version/SHA |
| `actions/upload-artifact` / `download-artifact` | target-repository approved version/SHA |
| `hashicorp/vault-action` | target-repository approved version/SHA |
| `hashicorp/setup-terraform` | target-repository approved version/SHA |

## 3. Shared scripts

Reuse cross-workflow logic via `common_*.sh` scripts under `.github/scripts/` (e.g. `common_terraform_init_backend.sh`, `common_run_ansible_playbook.sh`, `common_configure_ssh_key.sh`). Step scripts delegate rather than copy:

```bash
#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${DIR}/common_terraform_init_backend.sh"
```

### 3.1 Generalize by shape, not by step

One script per workflow step is the default drift, and it scales badly: a directory named `<workflow>_<job>_<step>.sh` reads as organised while being N copies of the same three commands. Group by *invocation shape* instead, and let the caller supply what differs.

Most CI scripts collapse into a handful of shapes — an `ansible-playbook` run, a `terraform` subcommand, an `ssh` action against a host resolved from the CMDB, a render/validate step. Audit by shape before adding another file:

```bash
for f in .github/scripts/*.sh; do
  grep -q 'ansible-playbook' "$f" && echo "playbook  $f" && continue
  grep -q 'terraform '       "$f" && echo "terraform $f" && continue
  grep -q 'ssh_opts='        "$f" && echo "ssh       $f"
done | sort | uniq -c
```

If a shape has more than two or three members, it wants one parameterised entry point. A set of playbook wrappers usually differs only in the playbook filename, how the target host is passed, and an optional extra-vars file — everything else, including the inventory path, is identical and should live in one place.

**The cost of not doing this is measured in repeated fixes.** When the same defect has to be patched in three sibling scripts, and a wrong inventory path in four, the duplication is not stylistic — each copy is a place the next guard will be forgotten. A shared entry point means the reachability assert (§8) and the required-variable check are written once and inherited by every caller.

**Standardise how the target is selected.** Passing the host as `-e "<role>_hosts=${HOST}"` and passing it as `--limit "${HOST}"` are not interchangeable: they fail differently when the value is empty. An empty `-e` var against a playbook whose `hosts:` reads from it aborts with "Keyword 'hosts' cannot have empty values", while an empty `--limit` against a playbook with a static `hosts:` line does not narrow anything. Pick one mechanism per repository so the empty case has one known behaviour, and assert the variable regardless (§8).

### 3.2 No hardcoded values in scripts

Anything that varies by environment, target, or release is a parameter. Domains, hostnames, IPs, zone names, registry namespaces and image tags belong in the caller's `env:` block or a single named constant — never inline in a script, and never as a per-file fallback.

- **A default that differs between files is worse than no default.** Divergent fallbacks produce output that is valid, plausible, and wrong in some files only, which is far harder to spot than a uniform failure. If several files each carry their own `X or 'some-domain'`, they will drift, and at least one will end up pointing at production.
- **Reject the "sensible default" for anything that selects a target.** A default target is a silent choice made on the operator's behalf at the exact moment they forgot to make one. Require it and fail (§8).
- **A literal that appears once is still a parameter if it varies by environment.** Judge by whether the value *could* differ per environment, not by how many times it currently appears.
- Values that genuinely never vary — a fixed image tag the pipeline itself builds, a path the pipeline itself creates — are implementation detail and may stay inline. Parameterising them adds indirection for no reuse.

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

### 7.1 CI and CD must be separate

CI establishes whether a revision is safe to promote; CD changes a managed
environment. They MAY share reusable scripts or callable workflows, but MUST
remain separate workflow boundaries, permissions, and success criteria.

| Concern | CI workflow | CD workflow |
| --- | --- | --- |
| Trigger | Pull requests and ordinary branch pushes | Only the repository's approved promotion event or an explicitly authorized dispatch |
| Purpose | Lint, test, render, validate, scan, and build | Consume a promoted release, deploy, migrate, verify, and report rollout state |
| Credentials | Read-only by default; no cloud mutation or production Vault role | Least-privilege OIDC/Vault role for the selected environment |
| Infrastructure | `terraform fmt`/`validate`/`plan` only | Explicitly confirmed `apply`, replacement, migration, or DNS action only |
| Artifact | Build once; publish immutable digest/version plus provenance | Download and verify the exact promoted digest/version; never rebuild from a moving ref |
| Failure meaning | Revision is not eligible for promotion | Environment did not reach the declared state; preserve diagnostics and rollback point |

- A CI workflow MUST NOT apply Terraform, mutate cloud resources, alter DNS,
  run production Ansible, or obtain deployment credentials. A green CI result is
  eligibility evidence, not a deployment claim.
- A CD workflow MUST consume an immutable artifact identity produced or approved
  by CI (digest, version, signed manifest, or plan artifact). Do not `checkout`
  an unconstrained branch tip and rebuild during deployment; that breaks the
  proof that was tested.
- Pass only explicit, typed promotion inputs across the boundary: revision SHA,
  artifact identity, target environment, approved action, and a correlation ID.
  Validate them at the CD entry point and record them in the deployment summary.
- Do not run untrusted pull-request code in a privileged context. In particular,
  `pull_request_target` and reusable workflows with deployment permissions need
  a reviewed, immutable caller/ref and must never execute PR-supplied scripts.
- Keep a separate deploy gate from the CI gate. Environment approval, concurrency,
  preflight, health checks, rollback, and post-deploy verification belong to CD;
  test/lint failures belong to CI. A CD workflow can call a narrow validation
  script, but must not be reported as “CI passed” if it skipped deployment.

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
- **An empty variable is not an error to the tool that receives it.** Variables that *select a target* or *carry a credential* fail silently when blank: an empty ansible host pattern or `--limit` matches zero hosts and exits `0`; `vault-action` with `ignoreNotFound` turns a renamed key into `""`, so `docker login` runs with an empty password and a Terraform backend gets `region=""` and dies several steps later, far from the cause. Assert them at the script's entry point rather than hoping a downstream command objects:
  ```bash
  require_env() {           # shared helper, sourced by every mutating script
    local missing=() v
    for v in "$@"; do [ -z "${!v:-}" ] && missing+=("$v"); done
    [ ${#missing[@]} -gt 0 ] && { echo "::error::missing: ${missing[*]}" >&2; exit 1; }
  }
  require_env MATRIX_HOST POSTGRES_ROOT_PASSWORD
  ```
  List only variables used *unconditionally* — making genuinely optional ones mandatory just to satisfy an audit trades one wrong behaviour for another.

## 9. Job gating must be falsifiable

A job that reports `skipped` looks identical whether it was deliberately not requested or is structurally incapable of running. That ambiguity hides broken gating indefinitely.

- **`needs.<job>` for a job absent from that job's `needs:` list evaluates to empty.** `'' == 'success'` is false, so the whole `&&` chain is false and the job never runs — no error, just a permanent `skipped`. Referencing a job that no longer exists at all does the same thing. Audit that every `needs.<x>` in an `if:` is both declared in `needs:` and defined in the workflow.
- **Distinguish "not requested" from "cannot run".** If a job is gated on an input, check the history: a job that is `skipped` on *every* run, including ones where the input was set, is not being skipped for the reason you think.
- **Conditions that coincide with the intent are still bugs.** A gate that evaluates false for the wrong reason can match the desired behaviour on the common path and diverge on every other one — e.g. a data-migration job whose `needs.provision.outputs.*` silently resolve to empty still skips correctly on deploy runs, and never runs at all on migrate runs.

## 10. Trigger scope

Triggers decide what a workflow costs and what it can damage. Both are easy to get wrong in the direction of "more".

- **A bare `push:` fires on every branch.** `on: push:` with no `branches`/`paths` runs for every push in the repo. When the sibling `pull_request:` block carries a `paths:` filter it is easy to misread as covering both — the filter applies only to the event it sits under.
- **State the blast radius of `pull_request`.** If the PR route runs `terraform apply` rather than `plan`, every pull request provisions real infrastructure that nothing tears down. Gate deploy jobs on the action (`terraform_action == 'apply'`) so routing a PR to `plan` disables them without touching their conditions.
- **Path filters must cover every input the job consumes.** A filter naming only `workflows/<x>.yaml` and `scripts/<x>_*` will silently skip the pipeline when a shared `common_*` script changes. Narrowing a deploy trigger is the same hazard class as §8: the run does not fail, it does not happen. Verify the filter against the actual set of files the job reads.
- **`paths` combined with a tag trigger is unreliable.** Do not add one to a release path without verifying tag pushes still run.

## 11. Before opening a PR

Run `bash -n .github/scripts/*.sh` and confirm `gitleaks` passes. Branch names and PR targets follow `project-development-standard`.

## 12. AI Workspace Infra workflow rules

- In `platform-ops-toolkit`, keep non-trivial logic in executable
  `.github/scripts/` files. Workflow `run:` entries invoke scripts; pass values
  via `env:`. Validate only the touched scripts with `bash -n`, parse touched YAML,
  and run the workflow's existing PR gate.
- Keep the domain-delivery sequence intact: render topology → Terraform → generate
  CMDB/inventory → upload/download CMDB artifact → Ansible. A replacement instance
  must be adopted into the original Terraform state before inventory generation.
- A normal `terraform apply` must reject a provider-incompatible plan change such
  as a Vultr in-place downgrade, then route the operator to an explicitly
  confirmed replacement workflow. Never hide provider errors with retries.
- New OIDC/Vault workflow files are a two-part change: workflow code plus the
  exact managed `job_workflow_ref` allowlist update. Verify both before dispatch.
- Scope concurrency by the actual mutable resource (environment and instance for
  resize; environment/domain for delivery). Do not cancel an in-progress stateful
  migration merely because a new run was requested.
- In `artifacts`, many existing image/chart workflows predate this layout. Make
  focused compatibility changes and audit `paths` filters against Dockerfiles,
  chart dependencies, and scripts actually consumed by the job.
