---
tags: [aws, foundations, vpc, subnet, route-table, security-group, nacl, nat, transit-gateway, vpc-endpoint, flow-logs]
aliases: ["VPC Deep Dive", "Subnets", "Security Groups", "NACLs", "NAT Gateway", "Transit Gateway", "VPC Peering"]
status: stable
updated: 2026-05-11
---

# VPC — Subnets, Routing, Security Groups, NACLs

> [!summary] Goal
> Master AWS networking: VPC CIDR, subnets (public/private), route tables, Internet Gateway, NAT Gateway, VPC Peering, Transit Gateway, VPC Endpoints, Security Groups vs NACLs, and VPC Flow Logs.

## Table of Contents

1. [VPC and CIDRs](#vpc-and-cidrs)
2. [Subnets and Route Tables](#subnets-and-route-tables)
3. [Internet and NAT Access](#internet-and-nat-access)
4. [Security Groups vs NACLs](#security-groups-vs-nacls)
5. [VPC Peering, Transit Gateway, and VPC Endpoints](#vpc-peering-transit-gateway-and-vpc-endpoints)
6. [VPC Flow Logs](#vpc-flow-logs)

---

## VPC and CIDRs

> [!info] VPC
> A Virtual Private Cloud is a logically isolated network within AWS. Each VPC has a CIDR block (primary, can add secondary), a default route table, a default security group, and a default NACL. VPCs span all AZs in a region.

```text
VPC limits per region:
  - VPCs:          5 (soft limit, can increase)
  - Subnets:       200 per VPC
  - Security groups: 2500 per VPC, 60 in/out rules per SG
  - NACLs:         200 per VPC, 20 rules per NACL (in/out each)
  - Route tables:  200 per VPC
  - Internet Gateways: 5 per region

CIDR considerations:
  - Use private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.
  - Size: /16 to /28 (min /28 per subnet = 11 usable IPs).
  - Always reserve space for: subnets, VPC Peering, TGW attachments.
  - Avoid overlapping CIDRs when peering/connecting VPCs.
```

---

## Subnets and Route Tables

> [!info] Subnet
> A subnet is a subdivision of the VPC CIDR within one AZ. Subnets are either public (route to IGW) or private (no direct IGW route). Each subnet has a single route table (can share across subnets).

```text
Subnet types:
  Public:  route table has 0.0.0.0/0 → Internet Gateway, auto-assign public IP enabled.
  Private: route table has 0.0.0.0/0 → NAT Gateway (or no internet access at all).
  Isolated: no route to NAT — cannot reach internet even indirectly.

Route table: prioritizes the most specific route (longest prefix match).
  - Local route: always exists (VPC CIDR → local).
  - IGW/NAT/TGW/Peering: for external destinations.

IP addressing in a subnet:
  AWS reserves 5 IPs per subnet (first 4, last 1).
  Example /24 subnet 10.0.0.0/24:
    10.0.0.0   — network address
    10.0.0.1   — VPC router
    10.0.0.2   — DNS server
    10.0.0.3   — Reserved for future use
    10.0.0.255 — broadcast (AWS doesn't support broadcast, but reserves the IP)
```

---

## Internet and NAT Access

### Internet Gateway (IGW)

```text
IGW is a horizontally-scaled, HA, managed VPC component.
  - Attached to a VPC (one IGW per VPC).
  - Enables communication between VPC and internet.
  - Target in route table: 0.0.0.0/0 → igw-id.
  - Also used for NAT Gateways (private subnets route traffic through NAT → IGW → internet).

No additional cost; pay only for data transfer through it.
```

### NAT Gateway vs NAT Instance

| Feature | NAT Gateway (managed) | NAT Instance (self-managed) |
|:--------|:---------------------:|:---------------------------:|
| **HA** | Within AZ (multi-AZ = one per AZ) | Scripted (use ASG, but complex) |
| **Bandwidth** | Up to 45 Gbps | Instance type dependent |
| **Maintenance** | None (AWS manages) | You manage (OS updates, patching) |
| **Cost** | Per hour + per GB processed | Instance cost + per GB (same data transfer) |
| **Source IP** | Same as IGW EIP | Same as IGW EIP (can assign multiple EIPs) |
| **Port forwarding** | Not supported | Supported (iptables) |
| **Bastion** | Not supported | Can be used as bastion |

```text
NAT Gateway sizing:
  - xlarge (assumed) → up to 45 Gbps.
  - Burst to 10 Gbps, then scales to 45 Gbps.
  - For > 45 Gbps: split into multiple AZs (one NAT Gateway per AZ).

Cost optimization:
  - One NAT Gateway per AZ is sufficient for most workloads.
  - Avoid data transfer between AZs if possible (traffic stays within region but cross-AZ costs apply).
  - Consider Gateway VPC Endpoints for S3/DynamoDB to avoid NAT data processing costs.
```

---

## Security Groups vs NACLs

> [!info] SG vs NACL
> Security Groups (SGs) are stateful firewalls attached to ENIs. Network ACLs (NACLs) are stateless firewalls attached to subnets. SGs are the primary defense; NACLs are secondary (default deny).

| Feature | Security Group | NACL |
|:--------|:--------------:|:----:|
| **Scope** | Instance/ENI level | Subnet level |
| **State** | Stateful (return traffic allowed automatically) | Stateless (must allow BOTH inbound and outbound) |
| **Rules** | Allow only (implicit deny everything else) | Allow AND Deny (number evaluation, lower = first) |
| **Order** | Rules evaluated as a whole (all rules apply) | Rules evaluated in order (lowest number first) |
| **Limit** | 60 in/out per SG | 20 per direction per NACL |
| **Use case** | Instance-level firewall | Additional subnet defense, explicit deny rules (e.g., block a specific CIDR) |

### Security group rules

```json
// SG for a web server:
Inbound:
  - HTTP  (80)   from 0.0.0.0/0
  - HTTPS (443)  from 0.0.0.0/0
  - SSH   (22)   from 10.0.0.0/16  (internal admin)
  - SSH   (22)   from 1.2.3.4/32   (bastion IP)

Outbound: all (0.0.0.0/0) — most SGs allow full outbound.

// Rule types:
//   - CIDR:  from 10.0.0.0/16, port 3306
//   - SG:    from sg-xxxx (any ENI with that SG can connect)
//   - Prefix list: from pl-xxxx (AWS-managed prefix like S3, DynamoDB)
```

### NACL rules

```json
// NACL for public subnet:
Inbound:
  100  HTTP   80   0.0.0.0/0     ALLOW
  200  HTTPS  443  0.0.0.0/0     ALLOW
  300  SSH    22   10.0.0.0/16   ALLOW
  310  SSH    22   0.0.0.0/0     DENY   // Block external SSH
  *    ALL    ALL  0.0.0.0/0     DENY   // Implicit deny

// Stateless — must also allow ephemeral ports for return traffic:
Outbound:
  100  TCP   32768-65535  0.0.0.0/0  ALLOW  // Ephemeral ports for HTTP responses
  *    ALL   ALL          0.0.0.0/0  DENY
```

---

## VPC Peering, Transit Gateway, and VPC Endpoints

### VPC Peering

```text
VPC Peering connects two VPCs (same or different account/region) via private IP.
  - Non-transitive: VPC-A ↔ VPC-B, VPC-A ↔ VPC-C does NOT give VPC-B ↔ VPC-C.
  - Overlapping CIDR: not allowed (routes conflict).
  - Same-region: free (no data transfer cost for inter-AZ within region).
  - Cross-region: charged for inter-region data transfer.

Limitations:
  - Cannot create peering between VPCs with overlapping CIDRs.
  - No transitive routing — use TGW for hub-and-spoke.
  - Edge-to-edge routing limitations: a peered VPC can't access the internet through another peered VPC (must add own IGW/NAT).
```

### Transit Gateway (TGW)

```text
TGW provides hub-and-spoke connectivity:
  - Attachments: VPC, VPN, Direct Connect, TGW Peering (cross-region).
  - Route tables per-attachment: isolate networks.
  - Route propagation: VPC routes automatically propagate.
  - Multicast support (for HPC applications).
  - Can be shared across accounts via AWS Resource Access Manager (RAM).

TGW vs Peering:
                    Peering           TGW
  Transitive         No                Yes
  Max connections    125 limitations   1000s of attachments
  Complexity         Simple            Moderate
  Cost               Free (same AZ)    Per hour + GB processed
  Cross-region       Yes               Yes (TGW Peering)
```

### VPC Endpoints

```text
VPC Endpoints allow private access to AWS services without traversing the internet.

Gateway Endpoints:
  - S3 and DynamoDB only.
  - Added as a prefix list in route table (no ENI, no additional cost).
  - Traffic stays within AWS network.
  - Use: ECR image pulls from ECS/EKS, S3 access from private subnets.

Interface Endpoints (AWS PrivateLink):
  - Powered by PrivateLink (ENI per subnet).
  - Support many services: SSM, STS, ECR, CloudWatch Logs, SQS, KMS, etc.
  - Cost: per hour + per GB processed.
  - Use: private subnets that need SSM Session Manager, ECR, CloudWatch, etc.

Gateway Load Balancer Endpoints — for traffic inspection (firewalls, IDS/IPS).
```

---

## VPC Flow Logs

> [!info] Flow Logs
> VPC Flow Logs capture IP traffic information (accepted/rejected). Published to S3 or CloudWatch Logs. Can be created at VPC, subnet, or ENI level. Useful for security analysis, troubleshooting, and cost attribution.

```text
Flow log fields (custom format):
  version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol,
  packets, bytes, start, end, action (ACCEPT/REJECT), log-status, vpc-id, subnet-id,
  instance-id, tcp-flags (FIN/SYN/RST/ACK/URG/PSH), type, pkt-srcaddr, pkt-dstaddr

Query with Athena (S3 destination):
  SELECT dstaddr, COUNT(*) as attempts
  FROM vpc_flow_logs
  WHERE action = 'REJECT'
  GROUP BY dstaddr
  ORDER BY attempts DESC
  LIMIT 10;
```

---

## Cross-Links

- [[CICD/AWS/03_Advanced/01_VPC_Deep_TGW_VPN_and_DirectConnect]] for VPC deep dive (TGW, VPN, DX)
- [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] for S3 Gateway Endpoint
- [[CICD/AWS/02_Core/03_ALB_NLB_and_Target_Groups]] for load balancers in VPC subnets
- [[CICD/AWS/04_Playbooks/03_Debug_VPC_and_Networking]] for troubleshooting
