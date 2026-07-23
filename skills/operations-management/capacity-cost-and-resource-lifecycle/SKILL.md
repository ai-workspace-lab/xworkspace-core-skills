---
name: capacity-cost-and-resource-lifecycle
description: Assess capacity, cost, resource ownership, VPS resizing, replacement, snapshots, reserved IPs, retirement, and cleanup. Use before changing cloud plans, disks, instance types, autoscaling, reservations, tags, budgets, snapshots, or lifecycle state.
---

# Capacity, Cost, and Resource Lifecycle

Treat a resource resize as a lifecycle change, not a simple plan edit. Provider capabilities, disk size, state ownership, data recovery, traffic routing, and cleanup are separate decisions.

## 1. Inventory and ownership

Every billable resource needs owner, service/environment, provider/account, Terraform address/state key, instance/resource ID, tags, cost center, creation reason, retention/expiry, backup class, and deletion authority. CMDB and Terraform are the runtime facts; spreadsheets or hand-maintained lists are not.

## 2. Capacity and cost preflight

Before change, capture observed CPU, memory, disk used/free, IOPS, network, error/latency headroom, backup size, growth forecast, monthly cost delta, and rollback capacity. Define the success condition and the duration of observation.

Provider plan changes must be classified before apply:

- In-place supported upgrade: create a rollback point, apply, then verify capacity and service health.
- Unsupported downgrade or disk shrink: create a replacement, restore application-level data, adopt Terraform state, regenerate CMDB/inventory, deploy, validate, then make an explicit traffic cutover.
- Snapshot restore: verify source size, target capacity, OS/architecture compatibility, provider constraints, and retention. A snapshot larger than the target disk is a rejected plan, not a retry candidate.

## 3. Cost controls

Set budgets and anomaly thresholds by account/environment/service. Review orphaned volumes, snapshots, IPs, load balancers, images, and stopped instances on a defined cadence. Automation may report candidates, but deleting billable or recoverable resources requires exact enumeration, owner confirmation, and a rollback/retention decision.

## 4. Retirement

Retire in stages: remove traffic, verify no consumers, retain recovery point for the approved window, export final audit metadata, then delete the exact resource IDs. Terraform state removal, provider deletion, DNS release, snapshot cleanup, and credential revocation are separate checklist entries; authorization for one does not imply authorization for the others.
