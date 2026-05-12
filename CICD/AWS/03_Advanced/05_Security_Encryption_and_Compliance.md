---
tags: [aws, advanced, security, encryption, compliance, kms, scp, guardduty, inspector, artifact, incident-response]
aliases: ["AWS Security Deep Dive", "Encryption at Rest", "SCPs", "Compliance", "Incident Response", "AWS Artifact"]
status: stable
updated: 2026-05-11
---

# Security — Encryption, Compliance, and Incident Response

> [!summary] Goal
> Master AWS security: encryption at rest/ in transit (KMS, ACM, TLS), IAM least privilege (access analyzer, permission boundaries, last access), SCPs (service control policies — region restrictions, root blocking), GuardDuty + Security Hub (finding pipeline), incident response procedure, AWS Artifact (compliance reports), and compliance frameworks (PCI DSS, HIPAA, SOC).

## Table of Contents

1. [Encryption — At Rest and In Transit](#encryption-at-rest-and-in-transit)
2. [IAM Least Privilege and SCPs](#iam-least-privilege-and-scps)
3. [Incident Response and Compliance](#incident-response-and-compliance)

---

## Encryption — At Rest and In Transit

### Encryption at rest

| Service | Default method | KMS integration |
|:--------|:-------------:|:---------------:|
| **S3** | SSE-S3 (AES-256) | SSE-KMS |
| **EBS** | Account-level default | KMS per volume |
| **RDS** | Enabled at launch | KMS per instance |
| **DynamoDB** | Enabled (default) | KMS (AWS managed or CMK) |
| **SQS** | SSE-SQS | SSE-KMS |
| **Kinesis** | Enabled (default) | KMS |
| **EKS** | etcd encryption | KMS (envelope) |

```text
Encryption by default:
  - EBS: enable at account level per region.
  - S3: enable `BucketKeyEnabled` (reduces KMS API cost).
  - RDS: enable encryption at launch (can't encrypt after launch).
  - KMS key policy: control who can encrypt/decrypt.

Best practice: enable encryption at rest for ALL services as the default.
Use customer managed KMS keys for compliance (audit key usage in CloudTrail).
```

### Encryption in transit

```text
TLS everywhere:
  - ALB/CloudFront: ACM certificates (public or private CA).
  - RDS: enforce TLS (rds.force_ssl=1).
  - S3: require `aws:SecureTransport` in bucket policy.
  - VPC: traffic between VPCs (VPC Peering/TGW) is encrypted by default.

TLS version: enforce TLS 1.2+ (block TLS 1.0/1.1 via bucket policy, ALB security policy).
```

---

## IAM Least Privilege and SCPs

### IAM Access Analyzer

```text
Access Analyzer identifies resources shared with external entities:
  - S3 buckets (public or cross-account), KMS keys, IAM roles (cross-account trust), SQS queues, Secrets Manager secrets.
  - Finding: resource, principal, action, condition.
  - Archive: mark as expected (prevents future alerts).

Unused access analyzer: finds IAM roles/users with unused permissions.
  - Recommends reducing policy scope based on last access.
  - Use: right-size IAM policies quarterly.
```

### Service Control Policies (SCPs)

```json
// SCP: deny root user actions (prevents root from disabling GuardDuty, CloudTrail, etc.)
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "guardduty:DeleteDetector",
                "cloudtrail:StopLogging",
                "cloudtrail:DeleteTrail"
            ],
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:PrincipalArn": "arn:aws:iam::*:root"
                }
            }
        }
    ]
}

// SCP: restrict regions (allow only us-east-1, eu-west-1)
{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
        "StringNotEquals": {
            "aws:RequestedRegion": ["us-east-1", "eu-west-1"]
        }
    }
}
```

---

## Incident Response and Compliance

### Incident response workflow

```text
1. Detect: GuardDuty finding, CloudWatch alarm, Security Hub finding, manual report.
2. Investigate: CloudTrail, VPC Flow Logs, Detective, GuardDuty findings history.
3. Contain: detach IAM policies, isolate EC2 (new SG with no rules), take EBS snapshot.
4. Eradicate: terminate compromised resources, rotate credentials (Secrets Manager).
5. Recover: restore from clean backup, apply updated security measures.
6. Post-mortem: update runbook, improve detection.

IAM containment: disable access keys, change password, apply deny-all policy.
EC2 containment: modify SG (remove all rules), take forensic snapshot.
S3 containment: apply bucket policy (deny all), enable CloudTrail data events.
```

### Compliance frameworks

```text
PCI DSS (payment card industry):
  - HSMs for key storage (CloudHSM or KMS with custom key store).
  - Encryption of cardholder data at rest.
  - Access control (IAM least privilege), audit trails (CloudTrail).
  - AWS Artifact: download PCI DSS compliance reports.

HIPAA (healthcare):
  - BAA with AWS (available through AWS Artifact).
  - Encryption at rest + in transit.
  - Access logging (CloudTrail, S3 server access logs).
  - GuardDuty for threat detection.

SOC (service organization controls):
  - SOC 1/2/3 reports in AWS Artifact.
  - Covers: data center physical security, access control, change management.

AWS Artifact: download compliance reports and agreements.
  - Reports: SOC, PCI, ISO, FedRAMP.
  - Agreements: BAA (Business Associate Addendum), DPA (Data Processing Addendum).

Automate compliance with:
  - Config rules + conformance packs: CIS, PCI DSS, AWS Foundational Security Best Practices.
  - Security Hub: aggregate findings, check security score.
```

---

## Cross-Links

- [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] for KMS key policies and envelope encryption
- [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] for CloudTrail and Config rules
- [[CICD/AWS/02_Core/08_WAF_Shield_and_Network_Security]] for WAF and Shield
- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for IAM policies and roles
