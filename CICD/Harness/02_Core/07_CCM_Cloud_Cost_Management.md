---
tags: [harness, core, ccm, cloud-cost, cost-perspective, budget, anomaly, recommendations, autostopping, k8s-rightsizing]
aliases: ["Harness Cloud Cost Management", "CCM Perspective", "CCM Budget", "CCM Anomaly", "AutoStopping Rule", "K8s Rightsizing"]
status: stable
updated: 2026-05-11
---

# Cloud Cost Management (CCM) — Cost Visibility and Optimization

> [!summary] Goal
> Master Harness CCM: perspectives (custom cost views), budgets (monthly/quarterly alerts), anomaly detection, recommendations (EC2 right-size, EBS volume type, K8s resource optimization, RDS idle), and auto-stopping rules (stop idle dev/stage instances automatically). Cover cost categories, connectors (AWS CUR, GCP BigQuery, K8s).

## Table of Contents

1. [CCM Connectors and Perspectives](#ccm-connectors-and-perspectives)
2. [Budgets and Anomalies](#budgets-and-anomalies)
3. [Recommendations and AutoStopping](#recommendations-and-autostopping)

---

## CCM Connectors and Perspectives

> [!info] CCM
> Cloud Cost Management models your cloud costs: AWS (via CUR in S3), GCP (via BigQuery), Azure (via billing exports), K8s (via OpenCost or cloud provider APIs). Perspectives group costs by region, account, environment tag, K8s namespace, or custom rules.

### CCM connectors

| Cloud | Connector type | Data source | Required IAM/permissions |
|:------|:---------------|:------------|:-------------------------|
| **AWS** | `AwsCC` | CUR (Cost and Usage Report) in S3 + access role | `cur:DescribeReportDefinitions`, `s3:GetObject`, `iam:PassRole` |
| **GCP** | `GcpCC` | BigQuery dataset | BigQuery data viewer |
| **Azure** | `AzureCC` | Billing export (storage account) | Reader on billing account |
| **K8s** | `CEK8sCluster` | Metrics + inventory from cluster | `kube-state-metrics` + metrics-server |

```yaml
# CCM perspective (group costs by team tag):
perspective:
  name: "Payment Team Monthly"
  identifier: payment_team_monthly
  viewRules:
    - tag:
        field: "Team"
        operator: EQUALS
        values:
          - "Payment"
    - tag:
        field: "Environment"
        operator: NOT_EQUALS
        values:
          - "dev"
  chartOfAccounts:
    - name: "Compute"
      budgetAmount: 50000
    - name: "Storage"
      budgetAmount: 10000
    - name: "Network"
      budgetAmount: 5000
```

---

## Budgets and Anomalies

> [!info] Budgets
> Budgets track actual vs planned spending. Anomaly detection uses ML to detect unusual cost spikes (e.g., a deployment that doubled EC2 instances unexpectedly).

```yaml
# Budget for a perspective:
budget:
  name: "Payment Team Monthly Budget"
  type: PERSPECTIVE_BUDGET           # Perspective-specific, or CUMULATIVE for account-wide
  scope: "payment_team_monthly"
  budgetAmount: 50000                 # $50,000 monthly
  period: MONTHLY                     # MONTHLY, QUARTERLY, YEARLY
  growthRate: 5                       # 5% monthly growth allowance
  alerts:
    - threshold: 80                   # Alert at 80%
      email: "oncall@company.com"
    - threshold: 100
      slackChannel: "#cost-alerts"
```

### Anomaly detection

```yaml
# Anomaly alert for a perspective:
anomaly:
  name: "Payment Team Anomaly"
  perspective: payment_team_monthly
  alertThreshold: 50                  # Alert if cost > 50% of expected
  notifyBy: SLACK
  slackWebhookRef: account.slack_webhook
  runDaysAfterCreation: 7              # Suppression window after creation
```

---

## Recommendations and AutoStopping

> [!info] AutoStopping
> AutoStopping rules stop non-production resources automatically based on schedule or idle detection. Supported resources: EC2 instances, RDS databases, ASGs, EC2-based VMs, ECS tasks, Lambda functions.

```yaml
# AutoStopping rule: stop dev EC2 if idle for 30min, restart at 9AM
autoStoppingRule:
  name: "dev-idle-stop"
  schedule:
    type: IDLE_TIME            # Stop when idle
    idleTime: 30               # Minutes of idle before stopping
    startTime: "09:00"         # Start (or re-start) at 9 AM
    endTime: "18:00"           # Stop at 6 PM if not used
    timezone: "America/New_York"
    days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
  resource:
    type: EC2
    spec:
      instanceId: i-xxx
```

### Rightsizing recommendations

```text
[Image: Harness UI → CCM → Recommendations]

K8s resource recommendations:
  - Container requests/limits rightsizing (based on actual usage).
  - Node pool optimization (right-size node types).
  - Recommendations include: requested CPU, actual CPU, requested memory, actual memory, savings estimate.

EC2 rightsizing:
  - Instance type over-provisioned (e.g., t3.2xlarge → t3.xlarge, save 50%).
  - Performance analysis based on CloudWatch metrics (CPU average, memory, network).
  - Savings amount and confidence score.

EBS recommendations:
  - Volume type change (gp2 → gp3, save 20%).
  - Delete unattached volumes.
  - Snapshot age and deletion recommendations.
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for CCM connector setup
- [[CICD/Harness/03_Advanced/01_AutoStopping_Rules_Savings_Plans_and_Rightsizing]] for advanced CCM
- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI cost tracking via CCM
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for cost dashboard alongside CD
