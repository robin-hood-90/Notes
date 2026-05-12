---
tags: [harness, advanced, sei, dora, deployment-frequency, lead-time, mttr, change-failure-rate, insights, value-stream]
aliases: ["Harness SEI", "DORA Metrics", "Engineering Insights", "Deployment Frequency", "Lead Time", "MTTR", "Change Failure Rate"]
status: stable
updated: 2026-05-11
---

# SEI — DORA Metrics and Engineering Insights

> [!summary] Goal
> Master Harness SEI (Software Engineering Insights): DORA metrics (deployment frequency, lead time for changes, mean time to recover, change failure rate), integrations (GitHub, GitLab, Jira, Jenkins, CircleCI, PagerDuty, SonarQube), value stream mapping, and insights profiles.

## Table of Contents

1. [DORA Metrics](#dora-metrics)
2. [Integrations and Value Streams](#integrations-and-value-streams)

---

## DORA Metrics

> [!info] DORA metrics
> SEI measures four key DORA metrics from your development toolchain. Integrates with: Git (commits through PROD deploy), CI/CD (build → test → deploy), Jira (ticket → commit), PagerDuty (incident → resolution).

| Metric | Definition | Elite | High | Medium | Low |
|:-------|:-----------|:-----|:-----|:-------|:----|
| **Deployment frequency** | Deploy count per week | Multiple/day | Once/week | Once/month | < once/month |
| **Lead time for changes** | Commit → PROD deploy | < 1 hour | < 1 week | < 1 month | > 1 month |
| **MTTR** | Incident → resolved | < 1 hour | < 1 day | < 1 week | > 1 week |
| **Change failure rate** | % deploys that fail | < 5% | < 10% | < 15% | > 15% |

### Configuring DORA metrics in SEI

```yaml
# SEI insight profile:
profile:
  name: "Platform Engineering DORA"
  identifier: platform_engineering_dora
  integrations:
    - provider: GITHUB
      connectorRef: account.github_org
      repos:
        - "my-org/payment-service"
        - "my-org/notification-service"
    - provider: JENKINS
      connectorRef: account.jenkins_connector
    - provider: JIRA
      connectorRef: account.jira_connector
    - provider: PAGERDUTY
      connectorRef: account.pagerduty
  doraSettings:
    deploymentFrequency:
      PRODStageKeys: ["Deploy to Prod"]    # Stage name in Harness pipeline
    leadTime:
      ticketToCommit: true                  # Jira ticket → git commit tracking
      commitToDeploy: true
```

---

## Integrations and Value Streams

> [!info] Value stream mapping
> SEI maps the end-to-end delivery process: ticket created → commit → build → test → deploy → incident → ticket closed. Value stream mapping shows where time is lost (long test times, slow approvals, long review cycles).

### Supported integrations

| Integration | Data collected |
|:------------|:---------------|
| **GitHub, GitLab, Bitbucket** | Commits, PRs, branches, reviews, merge time |
| **Jenkins, CircleCI, Harness CI** | Build times, test times, deploy times |
| **Jira, ServiceNow** | Ticket creation, ticket resolution |
| **PagerDuty, Opsgenie** | Incident detection, MTTR |
| **SonarQube, Snyk** | Code quality, security issues |

```yaml
# Value stream: lead time breakdown
leadTimeBreakdown:
  - stage: "Ticket Created to Commit"
    average: "2h 30m"
  - stage: "Commit to Build Start"
    average: "15m"
  - stage: "Build Duration"
    average: "8m"
  - stage: "Test Duration"
    average: "12m"
  - stage: "Deploy to Staging"
    average: "5m"
  - stage: "Approval Wait"
    average: "4h 20m"          # Wait for manual approval
  - stage: "Deploy to Prod"
    average: "3m"
```

[Image: Harness SEI → Dashboard → DORA Metrics Overview]

---

## Cross-Links

- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI metrics feeding SEI
- [[CICD/Harness/03_Advanced/02_SRM_SLOs_Error_Tracking_and_Change_Intelligence]] for incident-based MTTR
- [[CICD/Harness/03_Advanced/03_Internal_Developer_Portal_IDP]] for DORA scores in IDP scorecards
- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for connector setup
