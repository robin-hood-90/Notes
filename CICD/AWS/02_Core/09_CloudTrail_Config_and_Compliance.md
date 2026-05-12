---
tags: [aws, core, cloudtrail, config, guardduty, security-hub, inspector, macie, access-analyzer, detective, compliance]
aliases: ["CloudTrail Deep Dive", "AWS Config", "GuardDuty", "Security Hub", "Detective", "Compliance"]
status: stable
updated: 2026-05-11
---

# CloudTrail, Config, and Compliance

> [!summary] Goal
> Master AWS auditing and compliance: CloudTrail (management/data events, Insights, organization trails, log file validation), Config (rules, remediation, conformance packs, aggregation), GuardDuty (threat detection, finding types), Security Hub (security score, multi-account aggregation), Inspector (vulnerability scanning), and compliance frameworks.

## Table of Contents

1. [CloudTrail](#cloudtrail)
2. [Config](#config)
3. [GuardDuty and Security Hub](#guardduty-and-security-hub)

---

## CloudTrail

> [!info] CloudTrail
> CloudTrail records every AWS API call (who, when, what) for auditing, security analysis, and operational troubleshooting. Trails can be per-region or all-regions. Logs can be delivered to S3 and CloudWatch Logs.

```json
// CloudTrail log entry (simplified):
{
    "eventVersion": "1.08",
    "userIdentity": {
        "type": "AssumedRole",
        "arn": "arn:aws:sts::123456789012:assumed-role/Admin/i-abc123"
    },
    "eventTime": "2026-05-11T15:30:00Z",
    "eventSource": "ec2.amazonaws.com",
    "eventName": "RunInstances",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "203.0.113.42",
    "userAgent": "console.aws.amazon.com",
    "requestParameters": { "imageId": "ami-abc123" },
    "responseElements": { "instancesSet": { "items": [ { "instanceId": "i-xyz" } ] } }
}
```

### Event types

```text
Management events: control plane operations (CreateVPC, RunInstances, PutBucketPolicy).
  - Default: enabled trails capture management events.
  - Read-only vs write-only (separate or both).

Data events: resource operations within services.
  - S3: GetObject, PutObject, DeleteObject (high volume).
  - Lambda: Invoke.
  - DynamoDB: GetItem, PutItem (high volume).
  - Important but can be high-volume → use selective event selectors.

Insights events: anomalous API activity detection.
  - High volume of write management events (potential security incident).
  - Requires CloudTrail Insights to be enabled on the trail.
```

### Trail types

```text
Single-region trail: logs events for one region.
Multi-region trail: logs events for ALL regions (creates a trail in each region).
  - Recommended for security: one multi-region trail.
  - Cost: charged for log delivery in each region.

Organization trail: logs events for ALL accounts in the AWS Organization.
  - Created in management account, logs for all member accounts.
  - Member accounts cannot disable it (enforced in the organization).

Log file validation: SHA-256 hash files stored alongside logs.
  - Use: verify log integrity (no tampering).
  - Digest files: SHA-256 of each log file + digital signature.
```

---

## Config

> [!info] Config
> AWS Config records resource configuration changes, evaluates them against rules, and provides a timeline of changes. Rules can be AWS-managed or custom (Lambda). Config can auto-remediate non-compliant resources.

### Managed rules

```text
Common managed rules:
  - s3-bucket-ssl-requests-only
  - encrypted-volumes (EBS encryption)
  - restricted-ssh (no SG with SSH open to 0.0.0.0/0)
  - ec2-ebs-encryption-by-default
  - rds-storage-encrypted
  - cloud-trail-enabled
  - guardduty-enabled-centralized
  - iam-user-mfa-enabled
  - vpc-flow-logs-enabled

Custom rules (Lambda):
  - Check custom resource configurations (e.g., specific tag value).
  - Run complex evaluation that managed rules can't express.

Conformance packs: YAML-based template for deploying multi-rule packages.
  - Example: PCI DSS conformance pack, CIS AWS Foundations Benchmark.
```

### Remediation

```text
Config can auto-remediate non-compliant resources:
  - SSM Automation document: run a predefined remediation workflow.
  - Example: if an S3 bucket is public → apply SSM document to block public access.
  - Retry: configure maximum attempts and retry interval.
  - Auto-remediate: Config applies fix immediately on non-compliance detection.
```

---

## GuardDuty and Security Hub

### GuardDuty

> [!info] GuardDuty
> GuardDuty is a threat detection service that continuously monitors for malicious or unauthorized behavior. It uses integrated threat intelligence and ML to detect threats. Findings are categorized by severity (Low, Medium, High, Critical).

```text
Finding categories:
  - Backdoor: EC2 instance communicating with known C&C servers.
  - Behavioral: EC2 instance port scanning, unusual traffic patterns.
  - PenTest: Simulated penetration testing tools.
  - Recon: API calls from suspicious IPs, unusual IAM user behavior.
  - CryptoCurrency: EC2 instance that appears compromised for crypto mining.
  - Stealth: IAM user disabling CloudTrail/Config/GuardDuty.
  - UnauthorizedAccess: IAM user making API calls that fail repeatedly.

Suppression rules: filter out known false positives (set criteria by finding type, resource, severity).
```

### Security Hub

```text
Security Hub aggregates findings from multiple AWS services:
  - GuardDuty, Inspector, Macie, Firewall Manager, IAM Access Analyzer.
  - From partner integrations: 3rd-party security tools (CrowdStrike, Palo Alto, etc.).
  - Consolidate multi-account findings into a single dashboard.

Security score: % of passed security checks.
  - Based on enabled security standards: CIS AWS Foundations, PCI DSS, AWS Foundational Security Best Practices.

Automated response: EventBridge integration sends Security Hub findings to:
  - AWS Lambda (automated remediation).
  - PagerDuty, Slack (notifications).
  - Step Functions (complex remediation workflows).
```

---

## Cross-Links

- [[CICD/AWS/04_Playbooks/01_Debug_IAM_AccessDenied]] for CloudTrail IAM debugging
- [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] for compliance frameworks
- [[CICD/AWS/02_Core/08_WAF_Shield_and_Network_Security]] for WAF + Security Hub findings
- [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] for KMS audit with CloudTrail
