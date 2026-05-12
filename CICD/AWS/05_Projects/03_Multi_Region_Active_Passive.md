---
tags: [aws, project, multi-region, dr, failover, route53, dynamodb-global-tables, s3-crr, rds-read-replica]
aliases: ["Multi-Region Active Passive", "Disaster Recovery", "Route 53 Failover", "Global Tables"]
status: stable
updated: 2026-05-11
---

# Project: Multi-Region Active/Passive with Route 53 and DynamoDB Global Tables

> [!summary] Goal
> Build a multi-region architecture: primary region (us-east-1) running ECS + ALB + Auto Scaling, standby region (us-west-2) with same setup, DynamoDB Global Tables, S3 cross-region replication, Route 53 failover routing, and RDS cross-region read replica.

## Architecture

```text
Route 53 (failover routing) → Primary: us-east-1 ALB → ECS → DynamoDB (Global Table)
                             → Secondary: us-west-2 ALB → ECS → DynamoDB (Global Table)
                               ↑ Failover: R53 health check fails → route to secondary

S3: CRR from us-east-1 to us-west-2 (logs, assets)
RDS: cross-region read replica (standby for failover)
```

### Route 53 failover routing

```json
{
    "Comment": "Failover from us-east-1 to us-west-2",
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "api.example.com.",
                "Type": "A",
                "SetIdentifier": "primary",
                "Failover": "PRIMARY",
                "HealthCheckId": "hc-abc123",
                "AliasTarget": {
                    "HostedZoneId": "ZONEID",
                    "DNSName": "primary-alb-123.us-east-1.elb.amazonaws.com",
                    "EvaluateTargetHealth": true
                }
            }
        },
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "api.example.com.",
                "Type": "A",
                "SetIdentifier": "secondary",
                "Failover": "SECONDARY",
                "AliasTarget": {
                    "HostedZoneId": "ZONEID",
                    "DNSName": "secondary-alb-456.us-west-2.elb.amazonaws.com",
                    "EvaluateTargetHealth": true
                }
            }
        }
    ]
}
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/08_Route53_and_CloudFront]] for Route 53 failover routing
- [[CICD/AWS/01_Foundations/06_DynamoDB_NoSQL]] for DynamoDB Global Tables
- [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] for S3 CRR
- [[CICD/AWS/01_Foundations/05_RDS_and_Aurora]] for RDS cross-region read replica
