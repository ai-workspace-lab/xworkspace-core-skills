---
name: network-dns-tls-edge-management
description: Plan and operate DNS, TLS certificates, ACME, Caddy/Ingress/reverse proxies, edge routing, TTL, cutovers, validation, and rollback. Use before changing a public hostname, certificate, load-balancer route, ingress, proxy, firewall exposure, or DNS provider record.
---

# Network, DNS, TLS, and Edge Management

DNS and certificate changes are traffic-routing changes. Validate authoritative state and reachability before deploying a proxy or requesting a certificate; retries cannot repair NXDOMAIN or a wrong target.

## 1. Change record

For each public endpoint, record owner, canonical hostname, aliases, authoritative DNS zone/provider, record type/value, TTL, ingress/load-balancer target, certificate issuer, renewal owner, health endpoint, and rollback target.

## 2. Preflight

- Resolve A/AAAA/CNAME from authoritative and public resolvers. Confirm the desired record exists, points to the intended target, and has no conflicting IPv6/alias path.
- Confirm firewall/security-group/load-balancer reachability for the challenge and serving ports. Verify the edge target serves the expected health endpoint and virtual host.
- For ACME, validate DNS and challenge reachability before triggering Caddy/Ingress certificate issuance. Treat NXDOMAIN, stale AAAA, or inaccessible challenge traffic as a DNS/network change, not an application retry problem.
- Inspect certificate SANs, issuer, expiry, chain, redirect behavior, and application-level HTTPS health after change.

## 3. Cutover and rollback

1. State current target, desired target, TTL/propagation expectation, success signal, rollback target, and observation window.
2. Make the edge/proxy configuration and target healthy before DNS cutover.
3. Apply the smallest record/routing change, verify authoritative and public resolution, then validate TLS and user-facing health from independent locations.
4. Keep the previous route and certificate material available through the observation window. Roll back on declared health criteria, not on operator preference.

Do not delete old records, IPs, certificates, or hosts as part of the cutover unless explicitly approved after verification. Keep DNS credentials in Vault-backed workload identity; never put provider API keys in repository variables or logs.
