---
tags: [aws, playbook, vpc, networking, flow-logs, reachability-analyzer, connectivity, nat, nacl, tgw]
aliases: ["Debug VPC Networking", "VPC Troubleshooting", "Reachability Analyzer", "Flow Logs Analysis"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug VPC and Networking

> [!summary] Goal
> Diagnose AWS network connectivity issues: VPC Flow Logs analysis with Athena, Reachability Analyzer, NAT Gateway bandwidth, TGW routing, NACL vs SG conflicts, load balancer health check failures, and direct connect issues.

## Step-by-step

1. **Check security groups**: verify inbound/outbound rules allow the traffic.
2. **Check NACLs**: NACLs are stateless — ephemeral ports must be allowed for return traffic.
3. **Reachability Analyzer**: source/destination/return path check:
   ```bash
   aws ec2 create-network-insights-path --source i-xxx --destination i-yyy --protocol TCP --destination-port 443
   aws ec2 start-network-insights-analysis ...
   ```
4. **VPC Flow Logs**: query DENEID traffic with Athena:
   ```sql
   SELECT dstaddr, dstport, COUNT(*) FROM flow_logs WHERE action='REJECT' GROUP BY dstaddr, dstport;
   ```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC networking
- [[CICD/AWS/03_Advanced/01_VPC_Deep_TGW_VPN_and_DirectConnect]] for TGW and DX
- [[CICD/AWS/02_Core/04_ALB_NLB_and_Target_Groups]] for LB connectivity issues
