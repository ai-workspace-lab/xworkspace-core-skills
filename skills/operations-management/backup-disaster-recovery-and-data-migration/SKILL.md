---
name: backup-disaster-recovery-and-data-migration
description: Plan, implement, test, and audit backups, disaster recovery, VPS or cloud migrations, restore drills, RPO/RTO targets, data consistency, and retirement of old resources. Use before any recovery, replacement, resize, cross-cloud move, backup policy change, or destructive cleanup.
---

# Backup, Disaster Recovery, and Data Migration

A backup is not a recovery capability until a restore has met its declared RPO, RTO, integrity, and security requirements. Keep backup, migration, cutover, and cleanup as independently auditable phases.

Reference basis: [NIST contingency planning guidance](https://csrc.nist.gov/topics/security-and-privacy/security-programs-and-operations/contingency-planning) for coordinated recovery of systems, operations, and data after disruption.

## 1. Establish the recovery contract

For every critical service, define owner, data classes, dependency order, RPO, RTO, backup frequency, retention, encryption/key owner, restore destination, validation query, and last successful drill. Use the business impact to prioritize recovery; do not use a single generic target for all services.

## 2. Back up for restoration

- Capture application-consistent data: database logical/physical backup, object data, configuration, identity/Vault recovery material, and artifact/digest references as appropriate.
- Verify backup completion, encryption, retention, immutability/access separation, and restore readability. A successful upload alone is not verification.
- Never store backup credentials, unseal keys, or database passwords in Git, CI secrets, artifacts, or local temporary files. Use OIDC → Vault short-lived access.
- Track backup provenance: source instance ID, volume/data size, application version, timestamp, checksum or integrity result, and restore compatibility.

## 3. Drill restores

Run scheduled restores into an isolated target. Measure actual RPO/RTO, validate schema/application health and representative data, then destroy the drill target only after recording results. Treat a failed or overdue drill as a recovery risk, not an administrative task.

## 4. Migration and resize decision

1. Preflight source/target capacity, architecture, OS/runtime compatibility, required ports, DNS, and dependency order.
2. For in-place upgrades, take a verified rollback point and validate the provider supports the requested operation.
3. For downgrades, cross-cloud moves, or target disks smaller than the source, use application-level backup and restore. Do not assume a volume snapshot can restore to a smaller disk.
4. Create and verify the replacement; adopt it into Terraform state; regenerate CMDB/inventory; deploy configuration; run data and service health checks.
5. Cut traffic/DNS only through an explicit, reversible decision. Retain the source during an observation window, then enumerate and explicitly approve its deletion.

## 5. Recovery execution

Use a written runbook with preconditions, exact backup identifier, target scope, ordered dependencies, validation, rollback/abort point, and communication owner. Do not overwrite a healthy source or clear initialization state merely because a key file or local marker is missing; stop and make a recovery decision with evidence.

Record every migration or restore with source/target IDs, chosen backup, planned and actual RPO/RTO, validation evidence, DNS/cutover time, and old-resource cleanup approval.
