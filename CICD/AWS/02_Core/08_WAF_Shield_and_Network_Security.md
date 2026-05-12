---
tags: [aws, core, waf, shield, ddos, web-acl, managed-rules, rate-limiting, bot-control, network-firewall]
aliases: ["WAF Deep Dive", "Shield Advanced", "DDoS Protection", "WAF Rules", "Managed Rule Groups"]
status: stable
updated: 2026-05-11
---

# WAF, Shield, and Network Security

> [!summary] Goal
> Master AWS WAF: Web ACLs, rules (rate-based, IP, geographic, SQL injection, XSS, size constraint), managed rule groups (AWS Bot Control, OWASP Top 10), WAF logging, Shield Advanced for DDoS protection, and Network Firewall.

## Table of Contents

1. [WAF — Web ACLs and Rules](#waf-web-acls-and-rules)
2. [Shield — DDoS Protection](#shield-ddos-protection)
3. [Network Firewall](#network-firewall)

---

## WAF — Web ACLs and Rules

> [!info] WAF
> WAF is a web application firewall that protects HTTP(S) endpoints (ALB, CloudFront, API Gateway). It inspects HTTP/HTTPS requests and allows, blocks, or counts them based on rules.

### Rule types

| Rule type | Match criteria | Action |
|:----------|:---------------|:-------|
| **IP match** | Source IP CIDR | Allow/Block specific IP ranges |
| **Geographic** | Country of origin | Block traffic from specific countries |
| **Rate-based** | Requests per 5-min window per IP | Block IPs exceeding limit |
| **SQL injection** | `body`, `querystring`, `uri` for SQL patterns | Block SQL injection attempts |
| **XSS** | Cross-site scripting patterns | Block XSS attempts |
| **Size constraint** | Request body/header size | Block oversized requests |
| **Regex pattern** | Custom regex on any field | Custom attack patterns |
| **Label match** | Match from previous rule | Cross-rule coordination |

### Managed rule groups

```text
AWS managed rule groups (AWS Marketplace, no extra cost):
  - AWSManagedRulesCommonRuleSet: base OWASP (Core rule set).
  - AWSManagedRulesSQLiRuleSet: SQL injection.
  - AWSManagedRulesKnownBadInputsRuleSet: known malicious patterns.
  - AWSManagedRulesAmazonIpReputationList: IP reputation (spammers, scanners).
  - AWSManagedRulesAnonymousIpList: anonymous IPs (VPN, proxy, Tor).
  - AWSManagedRulesBotControlRuleSet: bot detection (Category and Targeted levels).
  - AWSManagedRulesAdminProtectionRuleSet: protect admin pages.

Capacity Units (WCU): each rule consumes 1–20 WCU based on complexity.
  - ACL capacity: default 1500, can be increased to 5000 (ACL) or per rule group.
```

### Rate-based rules

```yaml
# Rate-based rule: block an IP that exceeds 2000 requests in 5 minutes:
RateBasedRule:
  Type: AWS::WAFv2::Rule
  Properties:
    Name: RateLimit
    Priority: 0
    Statement:
      RateBasedStatement:
        Limit: 2000
        AggregateKeyType: IP
    Action: Block
    VisibilityConfig:
      SampledRequestsEnabled: true
      CloudWatchMetricsEnabled: true
      MetricName: RateLimit
```

---

## Shield — DDoS Protection

| Feature | Standard | Advanced ($3000/month) |
|:--------|:--------:|:----------------------:|
| **Network layer** | SYN flood, UDP flood | Same + enhanced detection |
| **Application layer** | No | Yes (WAF-based L7 DDoS mitigation) |
| **Cost protection** | No | Yes (credit for scaling costs) |
| **24/7 DRT access** | No | Yes (DDoS Response Team) |
| **AWS bill credits** | No | Yes (for DDoS-related scaling) |
| **Proactive engagement** | No | Yes (advance notification) |

---

## Network Firewall

> [!info] Network Firewall
> AWS Network Firewall is a managed stateful firewall for VPCs. It filters traffic at the network layer (L3-L7) using Suricata-based rules. It's deployed centrally with Transit Gateway.

```text
Rule types:
  - Stateful: Suricata rules (alert, pass, drop/reject), domain filtering, 5-tuple.
  - Stateless: simple allow/deny (like NACL).

Domain filtering: allow/block outbound connections to specific domains (e.g., block social media, allow only *.mydomain.com).

Traffic inspection: centralize egress traffic through a firewall VPC using Transit Gateway.
```

---

## Cross-Links

- [[CICD/AWS/02_Core/04_ALB_NLB_and_Target_Groups]] for WAF on ALB
- [[CICD/AWS/01_Foundations/08_Route53_and_CloudFront]] for WAF on CloudFront
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for WAF logging to CloudWatch
- [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] for overall security posture
