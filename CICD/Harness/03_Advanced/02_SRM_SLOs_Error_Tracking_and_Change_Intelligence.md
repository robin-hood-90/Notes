---
tags: [harness, advanced, srm, slo, sli, error-tracking, change-intelligence, monitored-service, health-source, dashboard]
aliases: ["Harness SRM", "Service Reliability Management", "SLO", "SLI", "Error Tracking", "Change Intelligence", "Monitored Service"]
status: stable
updated: 2026-05-11
---

# SRM — SLOs, Error Tracking, and Change Intelligence

> [!summary] Goal
> Master Harness SRM: service health (health score from SLOs), SLO definitions (availability/latency/custom SLI types, rolling window/ calendar periods, error budget), monitored services (connector → metric/deployment → health source), change intelligence (identify deployments causing SLO burns), and error tracking (APM, smart grouping).

## Table of Contents

1. [SLOs and SLIs](#slos-and-slis)
2. [Monitored Services and Health Sources](#monitored-services-and-health-sources)
3. [Change Intelligence and Error Tracking](#change-intelligence-and-error-tracking)

---

## SLOs and SLIs

> [!info] SLO
> A Service Level Objective (SLO) measures reliability over time. SLIs (Service Level Indicators) are metrics: availability (good requests / total), latency (fast requests / total), or custom (any ratio). Harness calculates error budgets and burn rates.

```yaml
# SLO definition:
slo:
  name: "Payment API Availability"
  identifier: payment_api_availability
  description: "Payment API should have 99.9% availability monthly"
  target:
    type: Rolling
    spec:
      periodLength: 28       # Rolling 28-day window
      target: 99.9
  sli:
    type: Availability
    spec:
      goodRequestMetric: "good_requests_total"
      totalRequestMetric: "total_requests_total"
      metricThreshold: 0.01   # 1% error budget rate alert
  tags:
    team: "payment"
    service: "payment-api"
```

### SLO types

| SLI type | Good request | Total request | Example |
|:---------|:-------------|:--------------|:--------|
| **Availability** | `http_requests_total{status=~"2.."}` | `http_requests_total` | API uptime |
| **Latency** | `http_request_duration_seconds{quantile="0.9"} < 0.5` | `http_request_duration_seconds_count` | p90 < 500ms |
| **Custom** | Any metric you define | Any total metric | Request throughput, error count |

### Error budget

```text
Error budget = (1 - SLO target) × total requests
  Example: 99.9% SLO = 0.1% error budget = 7.2 minutes per 5-day week.

Burn rate: how fast the error budget is consumed.
  - If error budget is consumed in 1 day when it should last 28 days → burn rate = 28.
  - Harness alerts when burn rate exceeds threshold (e.g., 2x for 1h, 10x for 5min).
```

---

## Monitored Services and Health Sources

> [!info] Monitored Service
> A monitored service connects telemetry data to a service in Harness. **Health sources** define which metrics come from which observability tool (Prometheus, Datadog, New Relic, AppDynamics, Splunk, Grafana, ELK, CloudWatch, Azure Monitor, etc.).

```yaml
# Monitored Service with Prometheus health source:
monitoredService:
  name: "Payment Service"
  identifier: payment_service
  type: Application
  serviceRef: payment_service
  environmentRef: production
  sources:
    - healthSource:
        name: "Prometheus Payment"
        identifier: prometheus_payment
        type: Prometheus
        spec:
          connectorRef: account.prometheus
          queries:
            - query: "rate(http_requests_total{application='payment-service'}[5m])"
              metricIdentifier: total_requests
              aggregation: "sum"
            - query: "rate(http_requests_total{application='payment-service', status=~'^2..'}[5m])"
              metricIdentifier: good_requests
              aggregation: "sum"
    - changeSource:
        name: "Harness CD"
        identifier: harness_cd
        type: HarnessCD25Plus   # Track deployment changes from Harness CD
```

---

## Change Intelligence and Error Tracking

> [!info] Change Intelligence
> Change Intelligence correlates deployments with SLO burns. When an SLO starts burning, SRM shows which deployment (from Harness CD, ArgoCD, K8s events, or any change source) caused the burn. This reduces MTTR by identifying the change that introduced the error.

### Change sources

```yaml
changeSource:
  - type: HarnessCD25Plus         # Harness CD deployments
  - type: K8sCluster             # K8s events (deployment rollouts)
  - type: ArgoCD                 # ArgoCD syncs
  - type: CustomWebhook          # Any change event via webhook
```

### Error tracking

```text
[Image: Harness SRM → Error Tracking → Payment Service → version comparison]

Error tracking with Harness APM:
  - Smart grouping: groups errors by stack trace (not just error message).
  - Version comparison: compare errors in current vs previous deployment version.
  - Stack trace: full stack trace with code links.
  - Error details: occurrence count, first seen, last seen, affected users.
```

---

## Cross-Links

- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI test results feeding SRM
- [[CICD/Harness/05_Projects/03_Multi_Stage_CI_CD_with_Security_and_SLO]] for SLO-based deployment validation
- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for health source connectors
- [[CICD/Harness/02_Core/06_Chaos_Engineering]] for chaos + SLO impact measurement
