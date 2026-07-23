---
name: service-catalog-and-runbook-standard
description: Create or review service catalog records, ownership metadata, dependency maps, operational runbooks, deployment records, backup and recovery references, and retirement documentation. Use when onboarding a service, changing ownership or dependencies, writing an operational procedure, or auditing operational readiness.
---

# Service Catalog and Runbook Standard

Every production service must have an operational record that lets a qualified responder identify ownership, impact, deployment path, dependencies, health, recovery, and safe escalation without tribal knowledge.

## 1. Minimum service record

Maintain a versioned record with: service name and purpose; business and technical owner; environment; repository and deploy entrypoint; immutable artifact/revision convention; public/internal endpoints; data classification; dependencies and dependency owners; SLO/dashboard/alerts; Vault role/path owner without secret values; CMDB/resource identity; backup/RPO/RTO; migration and retirement owner; and links to runbooks and recent incidents.

The record is metadata, not a second configuration source. Link to Terraform, CMDB, GitOps, workflow, and playbook sources rather than copying mutable IPs, credentials, or node lists.

## 2. Runbook requirements

Each operational action needs purpose, owner, trigger, prerequisites, exact target selection, least-privilege access path, commands/workflow link, expected output, validation, abort/rollback point, communication requirement, and evidence to retain. Mark whether the action is read-only, mutating, destructive, emergency-only, or legacy/manual.

Runbooks for restore, migration, DNS cutover, credential rotation, and deletion must name the explicit confirmation input and the recovery point. Do not hide a destructive action behind an ambiguous command such as `cleanup` or `reset`.

## 3. Keep records trustworthy

Update the service record in the same PR as a material ownership, endpoint, dependency, deployment, SLO, backup, or runbook change. Review records during incidents and quarterly operational reviews. A runbook that has not been exercised, whose target no longer resolves from CMDB, or whose owner is absent is stale and must be marked accordingly.

Link postmortem action items to the service record and runbook changes that prevent recurrence.
