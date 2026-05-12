---
tags: [aws, cicd, cloud, moc]
aliases: ["AWS MOC", "AWS Index", "AWS Learning Path"]
status: stable
updated: 2026-05-11
---

# AWS

> [!summary] Scope
> Complete AWS reference for CI/CD and production operations: IAM, EC2, VPC, S3, RDS, DynamoDB, Lambda, Route 53, CloudFront, SNS/SQS/EventBridge, API Gateway, ECS, EKS, ECR, ALB/NLB, CloudWatch, KMS, CloudFormation/CDK, WAF/Shield, CloudTrail/Config/GuardDuty, VPC Deep (TGW/VPN/DX), Cost Management, SSM/Session Manager/SSH, Autoscaling, Security/Compliance, and production playbooks.

## Foundations (10 files)

| File | Topics |
|:-----|:-------|
| **F01** [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] | Users/groups/roles, policy JSON (Effect/Action/Resource/Condition), trust policies, OIDC federation for CI/CD, permission boundaries, SCPs, cross-account access, policy evaluation logic |
| **F02** [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] | Instance families, purchasing options (on-demand/reserved/spot), AMI/user-data, EBS volumes/snapshots, placement groups, instance metadata |
| **F03** [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] | CIDR, subnets (public/private), route tables, IGW, NAT Gateway, Security Groups vs NACLs (stateful vs stateless), VPC Peering, Transit Gateway, VPC Endpoints, Flow Logs |
| **F04** [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] | Storage classes (Standard → Glacier Deep Archive), bucket policies vs IAM vs ACL, encryption (SSE-S3/KMS/C), versioning, Object Lock, lifecycle rules, replication (CRR/SRR), presigned URLs, event notifications |
| **F05** [[CICD/AWS/01_Foundations/05_RDS_and_Aurora]] | DB engines, Multi-AZ, read replicas, automated backups, manual snapshots, RDS Proxy, Aurora cluster volume (128TB, 6 copies across 3AZ), Aurora Serverless v2, Global Database |
| **F06** [[CICD/AWS/01_Foundations/06_DynamoDB_NoSQL]] | Partition/sort keys, LSI/GSI, on-demand vs provisioned capacity, DAX caching, DynamoDB Streams, Global Tables, single-table design (GSI overloading, adjacency list pattern) |
| **F07** [[CICD/AWS/01_Foundations/07_Lambda_Functions_Events_and_Best_Practices]] | Function config (memory/timeout/ephemeral), event sources (SQS/SNS/S3/DynamoDB/API Gateway/EventBridge), concurrency (reserved/provisioned), SnapStart, cold starts, VPC networking, versions/aliases/canary deployments |
| **F08** [[CICD/AWS/01_Foundations/08_Route53_and_CloudFront]] | Route 53: hosted zones, record types (A/AAAA/CNAME/MX/ALIAS), routing policies (simple/weighted/latency/failover/geolocation), health checks. CloudFront: origins, OAC, behaviors, TTLs, invalidations, Lambda@Edge vs CF Functions |
| **F09** [[CICD/AWS/01_Foundations/09_SNS_SQS_EventBridge_and_Messaging]] | SQS (standard/FIFO, DLQ, visibility timeout, long polling), SNS (standard/FIFO topics, fan-out, message filtering), EventBridge (event buses, rules, archive/replay, Pipes), Kinesis (Data Streams, Firehose, Data Analytics) |
| **F10** [[CICD/AWS/01_Foundations/10_API_Gateway_REST_HTTP_WebSocket]] | REST vs HTTP vs WebSocket, stages/usage plans/throttling, VTL mapping templates, Lambda/Cognito/IAM authorizers, canary deployments, API caching |

## Core (9 files)

| File | Topics |
|:-----|:-------|
| **C01** [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] | Fargate vs EC2, task definitions, services, rolling vs blue/green (CodeDeploy), Service Connect, ECS Exec, capacity providers, ECS Service Auto Scaling |
| **C02** [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] | Managed/self-managed/Fargate node groups, IRSA, Pod Identity, Karpenter vs Cluster Autoscaler, add-ons (VPC CNI, CoreDNS, EBS/EFS CSI), SGPP, upgrade workflows, KMS envelope encryption |
| **C03** [[CICD/AWS/02_Core/03_ECR_Scanning_and_Container_Registries]] | Private/public repos, immutable tags, basic + enhanced scanning (Inspector), lifecycle policies, pull-through cache rules, OIDC authentication for CI/CD |
| **C04** [[CICD/AWS/02_Core/04_ALB_NLB_and_Target_Groups]] | ALB (L7: host/path/query routing, WAF, auth, sticky sessions), NLB (L4: TCP/UDP/TLS, static IP), target groups (instance/IP/Lambda), health checks, mTLS, cross-zone balancing |
| **C05** [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] | Log groups/metric filters/structured logging, standard/custom metrics, alarms (static/anomaly/composite), Logs Insights (SQL-like), Synthetics canaries, Container Insights, Lambda Insights |
| **C06** [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] | KMS key policies, envelope encryption, auto rotation, multi-Region keys, CloudHSM custom key store. Secrets Manager: rotation with Lambda, cross-account access. Parameter Store: standard vs advanced tiers |
| **C07** [[CICD/AWS/02_Core/07_CloudFormation_and_CDK]] | Template anatomy, intrinsic functions (Ref/GetAtt/Sub/Join/Select/FindInMap), change sets, nested stacks, StackSets, drift detection. CDK: constructs (L1/L2/L3), synth/deploy, multi-environment pipelines |
| **C08** [[CICD/AWS/02_Core/08_WAF_Shield_and_Network_Security]] | Web ACL, managed rule groups (Bot Control, OWASP Top 10, IP reputation), rate-based rules, geographic match, bot detection. Shield Advanced (DDoS protection), Network Firewall (Suricata rules) |
| **C09** [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] | CloudTrail (management/data events, Insights, organization trail, log validation). Config (rules, conformance packs, auto-remediation). GuardDuty (finding types), Security Hub (aggregation), Inspector (vulnerability scanning) |

## Advanced (5 files)

| File | Topics |
|:-----|:-------|
| **A01** [[CICD/AWS/03_Advanced/01_VPC_Deep_TGW_VPN_and_DirectConnect]] | TGW (route tables, multicast, cross-region peering), Direct Connect (private VIF, transit VIF, LAG, MACsec), VPN (Site-to-Site BGP, Client VPN), PrivateLink, VPC Lattice, Reachability Analyzer |
| **A02** [[CICD/AWS/03_Advanced/02_Cost_Management_and_Optimization]] | Cost Explorer, Budgets (cost/usage/Coverage), Savings Plans (Compute/EC2 Instance), Reserved Instances, Compute Optimizer, Spot pricing, cost allocation tags, Trusted Advisor |
| **A03** [[CICD/AWS/03_Advanced/03_SSM_Session_Manager_and_SSH]] | SSH keys/pem/agent/config, bastion hosts (proxy jump, auto-scaling), EC2 Instance Connect (one-time key), SSM Session Manager (agent/IAM/VPC endpoints, port forwarding, session logging), SSH over SSM, comparison guide |
| **A04** [[CICD/AWS/03_Advanced/04_Autoscaling_ASG_and_TargetTracking]] | ASG (launch templates, target tracking/step/scheduled/predictive scaling), lifecycle hooks, cooldowns, ECS Service Auto Scaling (Fargate), Lambda concurrency (reserved/provisioned), DynamoDB auto scaling |
| **A05** [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] | Encryption at rest (KMS per service), encryption in transit (ACM/TLS), IAM Access Analyzer, SCPs (region restriction, root blocking), incident response workflow, compliance (PCI DSS, HIPAA, SOC), AWS Artifact |

## Playbooks (6 files)

| File | Topics |
|:-----|:-------|
| **P01** [[CICD/AWS/04_Playbooks/01_Debug_IAM_AccessDenied]] | Decode authorization message, CloudTrail analysis, IAM Policy Simulator, SCP/permission boundary checks, trust policy validation |
| **P02** [[CICD/AWS/04_Playbooks/02_Debug_ECS_EKS_Deployments]] | ECS stopped task reasons, deployment circuit breaker, EKS pod status (ImagePullBackOff, CrashLoopBackOff, Pending), IRSA/CNI errors |
| **P03** [[CICD/AWS/04_Playbooks/03_Debug_VPC_and_Networking]] | Reachability Analyzer, VPC Flow Logs (Athena), NACL vs SG conflicts, NAT bandwidth, TGW routing, Direct Connect troubleshooting |
| **P04** [[CICD/AWS/04_Playbooks/04_Debug_S3_and_CloudFront]] | S3 access denied (policy/IAM/ACL), CORS errors, presigned URL expiration, CloudFront cache invalidation, OAC misconfiguration |
| **P05** [[CICD/AWS/04_Playbooks/05_Debug_EC2_and_SSM]] | SSH connection refused (SG/key/user), SSM agent not connecting (VPC endpoints/IAM/agent status), user data logs (cloud-init), serial console |
| **P06** [[CICD/AWS/04_Playbooks/06_Cost_Investigation]] | Cost Explorer anomaly detection, data transfer costs, orphaned resources, Savings Plans coverage check, right-sizing recommendations |

## Projects (4 files)

| File | Topics |
|:-----|:-------|
| **Pr01** [[CICD/AWS/05_Projects/01_CI_CD_Pipeline_with_ECS_BlueGreen]] | GitHub Actions OIDC → IAM → ECR → ECS CodeDeploy Blue/Green with canary, test listener, auto-rollback |
| **Pr02** [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] | API Gateway REST → Cognito Auth → Lambda → DynamoDB, CloudFront, WAF rate limiting |
| **Pr03** [[CICD/AWS/05_Projects/03_Multi_Region_Active_Passive]] | Route 53 failover routing, ECS in 2 regions, DynamoDB Global Tables, S3 CRR, RDS cross-region replica |
| **Pr04** [[CICD/AWS/05_Projects/04_VPC_Private_Subnets_SSM_Fargate]] | VPC with public/private subnets, NAT Gateway, ECS Fargate in private subnets, SSM VPC Endpoints |

## Cross-Links

- [[CICD/GitHubActions/00_MOC/00_GitHubActions_MOC]] for CI/CD configuration
- [[CICD/Docker/00_MOC/00_Docker_MOC]] for container patterns
- [[CICD/Kubernetes/00_MOC/00_Kubernetes_MOC]] for K8s + EKS overlap
- [[CICD/Terraform/00_MOC/00_Terraform_MOC]] for IaC alternatives
- [[Networking/00_MOC/00_Networking_MOC]] for networking fundamentals

## References

- https://docs.aws.amazon.com/
- https://aws.github.io/aws-sdk-pandas/
