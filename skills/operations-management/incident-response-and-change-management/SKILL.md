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
