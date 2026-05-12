---
tags: [aws, advanced, vpc, transit-gateway, peering, vpn, direct-connect, privatelink, vpc-lattice, reachability-analyzer]
aliases: ["VPC Advanced", "Transit Gateway", "Direct Connect", "VPN", "PrivateLink", "VPC Lattice", "Reachability Analyzer"]
status: stable
updated: 2026-05-11
---

# VPC Deep — TGW, Peering, VPN, Direct Connect

> [!summary] Goal
> Master advanced AWS networking: Transit Gateway (hub-and-spoke, route tables, multicast), VPC Peering (limitations), VPN (Site-to-Site with BGP, Client VPN), Direct Connect (private VIF, transit VIF, LAG, MACsec), PrivateLink (service endpoints), VPC Lattice (service mesh), and Reachability Analyzer.

## Table of Contents

1. [Transit Gateway](#transit-gateway)
2. [Direct Connect](#direct-connect)
3. [PrivateLink and VPC Lattice](#privatelink-and-vpc-lattice)

---

## Transit Gateway

> [!info] TGW
> Transit Gateway connects thousands of VPCs and on-prem networks through a central hub. It supports VPC attachments, VPN attachments (DX and Site-to-Site), TGW peering (cross-region), and multicast domains.

```text
TGW route tables:
  - Each attachment can have its own route table.
  - Route propagation: automatically add CIDRs from attached VPCs.
  - Static routes: manually add for VPN, DX, peered TGWs.
  - Route evaluation: longest prefix match (like VPC route tables).

Attachment types:
  - VPC: attach from one or more subnets (per AZ).
  - VPN: Site-to-Site VPN connection.
  - Direct Connect: transit VIF via DX gateway.
  - TGW Peering: connect TGWs across regions.

Multicast domains:
  - Groups of EC2 instances that send/receive multicast traffic.
  - IGMPv2 protocol (group membership).
  - Use case: financial trading apps, video distribution.

Limits: 1000 attachments per TGW (can increase), 10 route tables per TGW.
Cost: per attachment per hour + per GB processed.
```

---

## Direct Connect

> [!info] DX
> Direct Connect is a dedicated network connection from your on-prem data center to AWS. It bypasses the public internet, providing consistent latency and higher bandwidth. Connection speeds: 50Mbps, 500Mbps, 1Gbps, 10Gbps, 100Gbps.

### Virtual interfaces (VIFs)

| VIF type | Connects to | Protocol | Use case |
|:---------|:-----------:|:--------:|----------|
| **Private VIF** | Single VPC (via VGW) | BGP over VLAN | Direct VPC access, no internet |
| **Transit VIF** | TGW (via DX Gateway) | BGP over VLAN | Multi-VPC access via TGW |
| **Public VIF** | AWS public services | BGP over VLAN | S3, DynamoDB, CloudFront (not common anymore) |

```text
Link Aggregation (LAG): bundle multiple connections for higher bandwidth and redundancy.
  - Up to 8 connections in one LAG.
  - All connections must be same speed (1G or 10G).

MACsec (802.1AE): Layer 2 encryption for DX connections.
  - Encrypts traffic between your router and AWS.
  - Uses a pre-shared connectivity association key (CAK and CKN).

Resiliency: multiple connections preferred (active/active or active/standby).
  - SiteLink: enable traffic between AWS regions via DX (bypass public internet).
```

---

## PrivateLink and VPC Lattice

### PrivateLink

```text
PrivateLink provides private connectivity between VPCs and AWS services.
  - Service consumer: create a VPC Endpoint (Interface) that connects to a service.
  - Service provider: create a Network Load Balancer and register it as a VPC Endpoint Service.

Cross-account PrivateLink:
  1. Provider creates a VPC Endpoint Service (NLB-based).
  2. Consumer creates a VPC Endpoint (Interface) to the service.
  3. Provider accepts the endpoint connection request.

Use cases:
  - Access third-party SaaS applications.
  - Publish your microservice as a private endpoint.
  - Connect VPCs in different accounts (without peering/TGW).
```

### VPC Lattice

```text
VPC Lattice is a fully managed service mesh for connecting, monitoring, and securing service-to-service communication across VPCs and accounts.

Service network: logical container for services.
Service: defined by listeners (HTTP/HTTPS) + target groups (EC2, ECS, Lambda, IP).
Auth policy: IAM policy (allow/deny) for service access.
Access logs: captured per service (S3, CloudWatch, Firehose).

Lattice vs Service Connect:
  - Lattice: cross-VPC, cross-account, IAM auth, centralized.
  - Service Connect: single ECS cluster, DNS-based, simpler.

Lattice Routing Categories:
  - Path-based, method-based, weighted (forward to multiple target groups).
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC basics
- [[CICD/AWS/04_Playbooks/03_Debug_VPC_and_Networking]] for TGW and DX troubleshooting
- [[CICD/AWS/05_Projects/03_Multi_Region_Active_Passive]] for TGW peering in multi-region
- [[CICD/AWS/05_Projects/04_VPC_Private_Subnets_SSM_Fargate]] for PrivateLink integrations
