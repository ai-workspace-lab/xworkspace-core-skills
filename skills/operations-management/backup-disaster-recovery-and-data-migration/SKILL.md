---
name: backup-disaster-recovery-and-data-migration
description: Plan, implement, test, and audit backups, disaster recovery, VPS or cloud migrations, restore drills, RPO/RTO targets, data consistency, and retirement of old resources. Use before any recovery, replacement, resize, cross-cloud move, backup policy change, or destructive cleanup.
---

# Backup, Disaster Recovery, and Data Migration

A backup is not a recovery capability until a restore has met its declared RPO, RTO, integrity, and security requirements. Keep backup, migration, cutover, and cleanup as independently auditable phases.

For generation replacement, read [Generation upgrade operational validation](references/generation-upgrade-validation.md)
for target protection, populated-data restore, actual incident regression cases,
writer handoff, and post-cutover reconciliation. The linked engineering skill
owns stage ordering and acceptance gates; this skill owns recovery procedures.

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
2. Classify upgrades using the engineering [UI/API/DB release rules](../../engineering-standards/multi-environment-delivery-and-release/SKILL.md#按变更类别选择发布方式). Database engine versions, SQL schema transitions, and upgrade data migrations require a new cluster, independent storage, and an empty target database. Vault Raft and other persistent-volume workload version/state transitions use the same replacement boundary. A backup or provider-supported operation does not authorize an in-place stateful business upgrade. UI/API code-only fixes and the explicitly independent non-business/non-billing monitoring service may follow their allowed in-place release path.
3. For downgrades, cross-cloud moves, or target disks smaller than the source, use application-level backup and restore. Do not assume a volume snapshot can restore to a smaller disk.
4. Create and verify the replacement; adopt it into Terraform state; regenerate CMDB/inventory; deploy configuration; run data and service health checks.
5. Cut traffic/DNS only through an explicit, reversible decision. Retain the source during an observation window, then enumerate and explicitly approve its deletion.

## 5. Recovery execution

Use a written runbook with preconditions, exact backup identifier, target scope, ordered dependencies, validation, rollback/abort point, and communication owner. Do not overwrite a healthy source or clear initialization state merely because a key file or local marker is missing; stop and make a recovery decision with evidence.

Record every migration or restore with source/target IDs, chosen backup, planned and actual RPO/RTO, validation evidence, DNS/cutover time, and old-resource cleanup approval.

## 6. Stateful upgrade execution and recovery

- Before migration, verify a protected source backup restores into isolation; retain a recoverable target baseline before modifying an existing candidate. After data copy, back up and restore a populated target and verify representative data, schema, permissions, and application connectivity. An empty-database restore alone does not establish business recovery.
- Initialize the reviewed SQL schema only on the new empty target, then use the business owner's fixed, validated migration tool (for example, `migratectl` where that is the existing owner tool). Pin its scope, version, schema checksums, source snapshot boundary, and target identity. Do not install or assume a particular CLI for unrelated systems. Keep target independent writers paused during transfer as required by its actual contract.
- Keep the source service, schema, and writer unchanged during candidate acceptance; read-only migration credentials do not freeze source business writes. Final catch-up, source-writer fencing, target-writer handoff, and traffic cutover require a separately reviewed operation within explicit authorization.
- Retry according to the actual tool contract. An empty-target-only copy is not an idempotent import into a populated database. After an uncertain result, inspect receipts and data first; never truncate/reset the target to make a retry pass. Prove rollback and emptiness before retrying an empty-target copy.
- Code/image rollback and SQL down migration do not prove data recovery. Preserve failed targets and evidence; recover into a separate isolated target from a verified backup or use an explicitly reviewed reconciliation procedure. Once a target accepts new writes, the old source is behind; switching traffic back does not restore those new facts.
