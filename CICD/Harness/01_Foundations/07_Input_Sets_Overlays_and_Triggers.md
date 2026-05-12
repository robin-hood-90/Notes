---
tags: [harness, foundations, input-sets, overlays, triggers, artifact-trigger, webhook-trigger, scheduled-trigger, notifications]
aliases: ["Harness Input Sets", "Harness Overlays", "Harness Triggers", "Webhook Trigger", "Scheduled Trigger", "Harness Notifications"]
status: stable
updated: 2026-05-11
---

# Input Sets, Overlays, and Triggers

> [!summary] Goal
> Master Harness input sets (pre-fill pipeline parameters for multiple environments), overlays (merge multiple input sets), triggers (artifact, webhook, scheduled, Git), and notifications (Slack, email, PagerDuty, webhook).

## Table of Contents

1. [Input Sets and Overlays](#input-sets-and-overlays)
2. [Triggers — Artifact, Webhook, and Scheduled](#triggers-artifact-webhook-and-scheduled)
3. [Notifications](#notifications)

---

## Input Sets and Overlays

> [!info] Input set
> An input set pre-fills runtime inputs for a pipeline. Instead of manually entering values each time a pipeline runs, you create input sets for common scenarios (e.g., `staging-params`, `prod-params`). An **overlay** merges multiple input sets together.

```yaml
# Pipeline with runtime inputs:
pipeline:
  name: "deploy-app"
  variables:
    - name: "environment"
      type: String
      value: <+input>         # Must be provided at runtime
    - name: "artifact_tag"
      type: String
      value: <+input>
  stages:
    - stage:
        type: Deployment
        spec:
          service: payment-service
          environment: <+pipeline.variables.environment>
          infrastructure:
            spec:
              namespace: payment-<+pipeline.variables.environment>

# Input set for staging (pre-fills variables):
inputSet:
  name: "staging-params"
  identifier: staging_params
  pipeline:
    identifier: deploy-app
    variables:
      - name: "environment"
        type: String
        value: "staging"
      - name: "artifact_tag"
        type: String
        value: "v1.2.3"

# Overlay: merge staging input set + prod input set:
inputSet:
  name: "staging-merge-prod"
  identifier: staging_merge_prod
  pipeline:
    identifier: deploy-app
    overlay:
      inputSetReferences:
        - "staging-params"
        - "prod-params"
```

---

## Triggers — Artifact, Webhook, and Scheduled

> [!info] Triggers
> Triggers start pipelines automatically based on events: new artifact push (ECR/Docker/GCR), Git webhook (push/PR/merge), cron schedule, or custom webhook.

### Artifact trigger

```yaml
trigger:
  name: "on-new-image"
  identifier: on_new_image
  type: Artifact
  spec:
    type: Docker
    spec:
      connectorRef: account.aws_ecr
      repoName: "my-app"
      eventType: "PushImage"
      tag: "*"                    # Match all tags
      # Exact tag: "main-v*"     # Glob pattern for tags
    pipelineRef: "deploy-app"
    inputSetRefs:
      - "staging-params"
```

### Webhook trigger (Git)

```yaml
trigger:
  name: "on-pr-merge"
  identifier: on_pr_merge
  type: Webhook
  spec:
    type: Github
    spec:
      event: "pull_request"
      actions:
        - "closed"                  # PR merged (closed = merged, not just closed)
      conditions:
        - key: "sourceBranch"
          operator: "Regex"
          value: "^(feature|fix)/.*"
        - key: "pullRequestAction"
          operator: "Equals"
          value: "closed"
      headerConditions:
        - key: "X-GitHub-Event"
          operator: "Equals"
          value: "pull_request"
    pipelineRef: "deploy-app"

# Webhook payload variables:
# <+trigger.webhook.payload.pull_request.number>
# <+trigger.webhook.payload.head_commit.message>
# <+trigger.webhook.payload.repository.full_name>
# <+trigger.webhook.gitUser>
```

### Scheduled trigger

```yaml
trigger:
  name: "nightly-build"
  identifier: nightly_build
  type: Scheduled
  spec:
    type: Cron
    spec:
      expression: "0 2 * * *"          # 2 AM daily
      timezone: "America/New_York"
    pipelineRef: "nightly-ci"
    inputSetRefs:
      - "nightly-params"

# Or rate-based (every N hours/minutes):
type: Rate
spec:
  interval: "1h"
```

---

## Notifications

> [!info] Notifications
> Send pipeline execution notifications to Slack, email, PagerDuty, or webhook. Configure per pipeline stage or at the pipeline level.

### Slack notification

```yaml
# Pipeline notification settings:
pipeline:
  notificationRules:
    - name: "deploy-failure"
      conditions:
        - type: StageFailed
          spec:
            stageNames:
              - "Deploy to Prod"
      notificationChannel:
        type: Slack
        spec:
          webhookUrl: <+secrets.getValue("slack_webhook_url")>
          userGroups:
            - account._account_all_users
      enabled: true

    - name: "deploy-success"
      conditions:
        - type: PipelineSuccess
      notificationChannel:
        type: Slack
        spec:
          webhookUrl: <+account.secrets.getValue("slack_webhook_url")>
```

### PagerDuty notification

```yaml
notificationChannel:
  type: PagerDuty
  spec:
    integrationKeyRef: account.pagerduty_key    # Secret reference
```

### Email notification

```yaml
notificationChannel:
  type: Email
  spec:
    userGroups:
      - account._account_all_users
    emailRecipients: ["oncall-team@company.com", "devops@company.com"]
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for storing triggers in Git
- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI triggers (PR merge webhook)
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for real trigger usage
