---
name: observability-slo-and-alerting
description: Define and operate SLIs, SLOs, error budgets, dashboards, alerts, telemetry correlation, and deployment verification. Use when onboarding a service, changing monitoring, tuning alerts, reviewing reliability, diagnosing a production issue, or deciding whether release velocity must be reduced.
---

# Observability, SLO, and Alerting

Measure user-visible outcomes, not merely process liveness. Alerts must be actionable, attributable, and linked to an owner and runbook.

Reference basis: [Google SRE error-budget policy](https://sre.google/workbook/error-budget-policy/) for release/reliability decisions, and [OpenTelemetry log correlation](https://opentelemetry.io/docs/specs/otel/logs/) for connecting logs, traces, and metrics through shared execution and resource context.

## 1. Service reliability contract

For each production service, declare owner, users/journey, critical dependencies, SLI source, SLO target/window, error-budget policy, alert thresholds, dashboard, and runbook. Choose SLIs that reflect the service: availability, latency, correctness, freshness, saturation, or successful asynchronous delivery.

An SLO without a measurable query, owner, and response policy is documentation, not an operational control. Use error-budget consumption to decide release velocity, canary progression, and reliability work priority.

## 2. Telemetry design

- Emit metrics, logs, and traces with consistent service, environment, revision/digest, region, and instance/resource identity.
- Propagate trace context and include trace/span identifiers in logs where supported. Do not put credentials, raw personal data, database connection strings, or high-cardinality unbounded values in labels.
- Keep a dashboard for golden signals and dependencies: traffic, errors, latency, saturation, resource capacity, background-job freshness, DNS/TLS expiry where relevant, and deploy/change markers.

## 3. Alert policy

| Severity | Meaning | Required response |
| --- | --- | --- |
| Page | Active or imminent user/data/security impact | On-call acknowledgement, incident path, runbook |
| Ticket | Action needed but not urgent | Owner, due date, trend/watch query |
| Info | Context or audit event | No human interruption by default |

Every page needs an owner, escalation path, symptom, impact threshold, dashboard link, runbook, and a clear resolve condition. Test alert routing and silence expiry. Avoid alerts that only report a known deployment or lack a response action.

## 4. Deploy and incident verification

Before a production rollout, define the baseline and success/error signals. During rollout, compare the promoted revision with baseline SLI, logs/traces, and dependency health. After rollout, record the observation window and rollback threshold. A deployment is not successful because the workflow exited zero; it must meet the declared service health criteria.

Review noisy, missing, and stale alerts after incidents. Link material incidents to SLO/error-budget impact and corrective work.
