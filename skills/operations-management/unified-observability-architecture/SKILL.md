---
name: unified-observability-architecture
description: Architectural constraints, collector responsibilities, telemetry topologies, reliability contracts, and GitOps governance for unified observability across edge hosts, container platforms (Kubernetes/K3s), and central observation planes. Use when designing, deploying, reviewing, or debugging observability collectors (vmagent, Vector, OTel), remote write pipelines, log/trace delivery, or evaluating collector necessity and boundaries.
---

# Unified Observability Architecture

All systems must stream telemetry to a centralized, persistent observation plane under uniform architectural constraints, decoupled collector responsibilities, and zero-leak credential governance. Telemetry must be collected actively, buffered reliably against network partitions, and governed through declarative GitOps profiles without fragmented edge storage silos.

Reference basis: [OpenTelemetry Collector Architecture](https://opentelemetry.io/docs/collector/architecture/) for decoupled processing pipelines, and [VictoriaMetrics High-Availability Remote Write Guidelines](https://docs.victoriametrics.com/vmagent/) for robust telemetry buffering and streaming across network boundaries.

## 1. Collector Responsibility and Topology Profiles

Adopt specialized or converged collector patterns based strictly on runtime capabilities, scheduling form, and operational scale. Do not replace mature, specialized tools for superficial homogeneity.

- **Edge / VPS / VM / Bare Metal Profile (Converged)**:
  - Default to a converged collector pattern (Vector All-in-One).
  - A single lightweight agent handles both host metrics (scraping static local exporters) and system/application logs (journald, log files).
  - Keep the footprint minimal; do not introduce dedicated metric scrapers unless distinct edge topology or high-throughput cardinality demands it.
- **Container / Kubernetes Profile (Specialized)**:
  - Enforce strict specialization between metrics and logs to honor Kubernetes dynamic lifecycle and service discovery:
    - **`vmagent` (Metrics Specialist)**: Dedicated to scraping, filtering, and remote-writing Prometheus/OpenMetrics data. Owns Kubernetes Service Discovery (`kubernetes_sd_configs` for pods, nodes, endpoints), Kubelet/cAdvisor authenticated scrapers, and dynamic relabeling.
    - **`Vector` (Logs Specialist)**: Dedicated to tailing, transforming, and streaming container logs, journald, and host logs.
  - Collector responsibilities are strictly orthogonal. Never configure duplicate scraping or overlapping delivery for the same telemetry class.
  - Never attempt to replace Kubernetes-native metric scrapers with log processors lacking dynamic API service discovery.
- **Distributed Tracing (On-Demand)**:
  - Deploy OpenTelemetry (OTel) Collector selectively when application tracing is required.
  - Tracing collectors must not displace or duplicate established metrics or logs pipelines.

## 2. Centralized Observability and Anti-Silo Mandate

- **Single Ingestion and Persistence Authority**:
  - The central observability platform is the single authoritative sink for storage, cross-cluster correlation, alerting, and visualization.
  - Telemetry is pushed actively from edges and clusters to central ingestion gateways over HTTPS.
- **Prohibition of Edge Storage Silos**:
  - Edge hosts and application clusters must **never deploy local, ad-hoc time-series databases or mock sinks** (e.g., local Prometheus server, standalone VictoriaMetrics instances) as permanent or staging components.
  - Rely exclusively on collector-native disk queues for network partition resilience; do not wrap redundant storage engines around collector agents.
- **Protocol Standardization**:
  - **Metrics**: Prometheus / VictoriaMetrics Remote Write protocol (`/api/v1/write`).
  - **Logs**: Native bulk HTTP or JSON line ingestion protocols supported by the central log backend.
  - **Traces**: Standard OTLP (gRPC or HTTP) ingestion.

## 3. Reliability, Resilience, and Network Partitioning

- **Durable Local Buffering**:
  - All collectors sending cross-network telemetry must configure bounded, non-volatile disk buffers (e.g., disk queues with explicit size limits).
  - In the event of WAN interruption, rate limiting, or central gateway unavailability, collectors must buffer data on disk in-order and replay with backoff upon restoration, without blowing up memory or dropping samples.
- **Metric Cardinality and Relabel Governance**:
  - Apply metric relabeling at the edge before transmission. Drop high-cardinality unbounded labels, runaway file-descriptor probes, and non-actionable histogram buckets before remote write.
  - Inject source identity, environment, cluster name, and workload namespace through verified relabel rules or trusted runtime receipts. Do not fabricate synthetic candidate labels.

## 4. Security, Identity, and Credential Governance

- **Transport and Edge Authentication**:
  - All cross-network telemetry streams must be encrypted via TLS.
  - Central ingestion gateways must enforce strict authentication (e.g., HTTP Basic Auth or Bearer tokens) at the perimeter.
- **Zero Credentials in Git**:
  - Telemetry ingestion credentials must originate from centralized secrets management (Vault) via short-lived workload identity or Kubernetes ExternalSecrets.
  - Never commit collector passwords, tokens, or private ingress credentials into declarative GitOps manifests.
- **Telemetry Sanitization**:
  - Scrub sensitive values, connection strings, personal identifiers, and credentials from log streams and trace attributes before egress.

## 5. GitOps Architecture and Code Agent Decision Boundaries

- **Profile-Driven Declarations**:
  - Maintain reusable, environment-independent GitOps declarations structured by profile (`edge-profile`, `kubernetes-profile`).
  - Keep collector manifests, exporter releases, and ingress identities decoupled to allow independent upgrades and rollbacks.
- **Code Agent Verification Discipline**:
  - Code Agents must **investigate first, decide second, and implement third**.
  - Must confirm live host/cluster topology, existing collector processes, central gateway reachability, and authenticated write paths before making declarative changes.
  - Strict prohibitions:
    - Never apply template configurations without discovering the actual runtime environment.
    - Never introduce new collectors, proxies, or storage sinks without verified architectural need.
    - Never replace stable, working collector configurations merely for superficial consistency.
    - Clean up and purge all temporary test sinks, stubs, and mock endpoints before promoting changes to production.
