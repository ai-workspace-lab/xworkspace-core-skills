---
name: incident-response-and-change-management
description: Manage production incidents, emergency changes, rollout freezes, recovery decisions, incident timelines, blameless postmortems, and corrective-action closure. Use when a service is degraded, a deployment or infrastructure change fails, an urgent change is requested, or an operational incident needs coordination.
---

# Incident Response and Change Management

Treat customer impact, data loss, security exposure, and uncontrolled blast radius as incidents. Stabilize first; diagnose second; improve last. Never use an incident as authority to bypass access controls, erase evidence, or make an unreviewed destructive change.

Reference basis: [Google SRE error-budget policy](https://sre.google/workbook/error-budget-policy/) for balancing reliability work, release decisions, and post-incident follow-up.

## 1. Declare and control

1. Classify severity from user impact, data/security impact, affected scope, and time sensitivity. Record the rationale and time.
2. Name one incident commander, one technical lead, and one communications owner. The incident commander owns scope and change approval, not every technical action.
3. Freeze unrelated production changes for the affected service/environment. Permit only containment, rollback, evidence preservation, and explicitly approved recovery changes.
4. Start a timestamped timeline with symptom, detection source, affected services, current hypothesis, commands or workflows run, and decisions. Never put credentials in it.

## 2. First response

- Confirm the impact with independent evidence: health endpoint, synthetic request, error rate, deployment state, DNS/certificate state, or provider status.
- Prefer reversible containment: stop rollout, disable the new route, scale a known-good version, or restore a previous DNS target. Do not restart, delete, truncate, or reinitialize merely to make an alert disappear.
- Capture safe diagnostics before changing state: revision/digest, Terraform plan/state reference, CMDB instance ID, relevant service status, and error excerpts with secrets redacted.
- Require explicit confirmation before DNS cutover, source-instance deletion, data restore, key rotation, or state removal even during an incident.

## 3. Change classes

| Class | Use | Minimum gate |
| --- | --- | --- |
| Standard | Repeated, low-risk, documented action | Approved runbook and preflight evidence |
| Normal | Planned state or behavior change | PR/review, rollback, maintenance window where needed |
| Emergency | Active incident containment or recovery | Incident commander approval, recorded rationale, retrospective review |

Emergency does not mean unlogged. It means the approval is time-bound and recorded in the incident timeline.

## 4. Recover and verify

- State the desired recovery condition before acting: availability, correctness, data freshness, certificate validity, or fleet reachability.
- Verify recovery at the user-facing boundary and the dependency boundary; a green process or CI job is not sufficient.
- Keep rollback assets and the previous resource until the declared observation window is complete. Record the owner and expiry of the cleanup decision.
- Close only after monitoring is stable, the communication status is updated, and every emergency change has a durable configuration/IaC representation or an explicit revert plan.

## 5. Blameless postmortem and action closure

Publish a factual, blameless postmortem for material incidents. Include impact, detection, timeline, contributing system conditions, what worked, what did not, and concrete actions. Actions need an owner, priority, due date, acceptance test, and link to the implementation PR or runbook. Do not close an action because a document was written; close it when the preventive control is verified.

Route configuration, Terraform, CI/CD, Vault, DNS, and backup changes to their owning standards. Use error-budget consumption and repeated incident class to decide whether to freeze releases or prioritize reliability work.

## 6. Fault-change closure loop

Every material release or operational fault MUST close through one traceable loop:

```text
impact -> containment -> evidence -> bounded change -> review/approval
       -> CI/preflight -> deployment -> boundary verification
       -> monitoring window -> postmortem action closure
```

The incident record must preserve the triggering release/tag, source SHA,
environment route, workflow/PR links, Vault role/path used, test and health
evidence, rollback point, and the owner plus expiry of any cleanup decision.
Do not declare recovery from a green process or downstream UI alone; verify the
user-facing boundary and each relevant dependency boundary. If the corrective
change is made during an incident, represent it in the owning repository through
the normal PR/release path or record an explicit revert plan and follow-up owner.

An action is closed only when its preventive control has passed its acceptance
test and the evidence is linked back to the incident. A document, a successful
workflow dispatch, or an unchanged dashboard is not closure evidence by itself.

## 6.1 Scheduled repository hygiene

Treat release-reference and branch cleanup as a normal, auditable change rather than an ad-hoc deletion. Run a read-only inventory weekly and retain its output as evidence.

- Permanently preserve stable `v*` release tags; never move, overwrite, or delete them. Protect them with repository rulesets where available.
- Preserve all build/environment tags from the configurable recent window `RECENT_RETENTION_DAYS` (default: 7 calendar days) and at least one deployable rollback tag per environment/service.
- Protect `main`, `master`, `develop`, and `release/*` permanently; prohibit force-push, ref replacement, and deletion. Preserve every branch that is not archived within the configurable recent window `RECENT_RETENTION_DAYS` (default: 7 calendar days), as well as branches with open PRs, active deployment references, or explicit retention labels.
- A branch is eligible for deletion only when it is archived, merged into the default branch, has no open PR, has no active deployment reference, and has passed the configured grace period. Unknown archive, merge, or deployment state means keep it.
- Before deletion, publish the exact candidate refs, classification, reason, repository, operator, and timestamp. Use explicit ref names; never delete with a broad wildcard.
- After deletion, re-fetch with pruning and verify protected refs, retained rollback references, and the deletion result. Preserve local worktrees, local branches, and uncommitted files.
- Review the retention exceptions monthly and assign an owner and expiry to every exception.
