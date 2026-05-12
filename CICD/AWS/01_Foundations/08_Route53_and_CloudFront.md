---
tags: [aws, foundations, route53, cloudfront, dns, cdn, alias-records, routing-policies, waf, lambda-edge, certificate-manager]
aliases: ["Route 53", "CloudFront", "DNS Routing", "CDN", "Alias Records", "CloudFront Functions", "WAF on CloudFront"]
status: stable
updated: 2026-05-11
---

# Route 53 and CloudFront — DNS and CDN

> [!summary] Goal
> Master Route 53 DNS: hosted zones, record types (A/AAAA/CNAME/ALIAS), routing policies (simple, weighted, latency, failover, geolocation), health checks, and Domain registration. Master CloudFront CDN: distributions, origins, behaviors, TTL, invalidations, signed URLs, Lambda@Edge, CloudFront Functions, WAF integration, and origin shield.

## Table of Contents

1. [Route 53 — DNS](#route-53-dns)
2. [CloudFront — CDN](#cloudfront-cdn)

---

## Route 53 — DNS

> [!info] Route 53
> Route 53 is AWS's scalable DNS and domain registration service. It translates domain names to AWS resources (ALB, CloudFront, EC2, S3) via routing policies.

### Record types

| Type | Purpose | Alias support |
|:----:|:--------|:-------------:|
| **A** | Map domain → IPv4 | Yes (ALIAS only for AWS resources) |
| **AAAA** | Map domain → IPv6 | Yes |
| **CNAME** | Map domain → another domain | No (not at zone apex) |
| **MX** | Email routing (mail exchange) | No |
| **TXT** | Text records (SPF, DKIM, domain verification) | No |
| **NS** | Name servers for delegation | No |
| **ALIAS** | Route53-specific: CNAME-like but works at zone apex | N/A (always to AWS resource) |

### Routing policies

| Policy | Use case | Health check support |
|:-------|:---------|:--------------------:|
| **Simple** | Single resource (default) | No |
| **Weighted** | Canary deploys, A/B testing, traffic splitting | Yes |
| **Latency** | Route to lowest-latency region | Yes |
| **Failover** | Active-passive DR | Yes (primary health check) |
| **Geolocation** | Route based on user location | Yes |
| **Geoproximity** | Route based on resource location + bias | Yes |
| **Multi-value** | Return multiple healthy IPs (simple HA) | Yes |

### Health checks

```text
Type 1: Endpoint — check IP/domain (HTTP, HTTPS, TCP).
Type 2: Calculated — combine child health checks (OR, AND, at most N unhealthy).
Type 3: CloudWatch alarm — check CloudWatch metric.

If health check fails, Route 53 removes the record from responses (for weighted/latency/failover).
```

---

## CloudFront — CDN

> [!info] CloudFront
> CloudFront is a global content delivery network (CDN) that speeds up distribution of static and dynamic content. It uses edge locations (450+ POPs) to cache content closer to users. Integrates with WAF, Shield, Lambda@Edge, and CloudFront Functions.

### Distribution types

| Type | Content | Protocol | Use case |
|:----:|:--------|:--------:|----------|
| **Web** | HTTP/HTTPS | HTTP/1.1, HTTP/2, HTTP/3 | Static websites, APIs (pairs with ALB/S3) |
| **RTMP** | Streaming | RTMP | Deprecated — use MediaLive |

### Origins

```text
An origin is where CloudFront gets content:
  - S3 bucket (static content, with OAC — Origin Access Control).
  - ALB / EC2 / HTTP server (dynamic content, custom origin).
  - Lambda function URL.
  - S3 website endpoint (for S3 static website hosting).

Origin groups: primary + secondary for failover.

Origin access control (OAC): restricts S3 access to only CloudFront distributions (OAC is newer than OAI).
```

### Behaviors

```text
Behaviors define how CloudFront handles requests based on path pattern:
  - Path pattern: /images/*, /api/*.
  - Viewer protocol: HTTP+HTTPS, HTTPS-only (redirect HTTP→HTTPS).
  - Allowed HTTP methods: GET/HEAD (static), GET/HEAD/OPTIONS/PUT/POST/PATCH/DELETE (dynamic API).
  - Cache policy: TTL min/default/max, query string/header/cookie forwarding.
  - Origin request policy: what headers/cookies/query strings to include from the viewer.
  - Response headers policy: CORS, security headers (HSTS, X-Content-Type-Options).
  - Lambda@Edge / CloudFront Function associations.

Cache invalidation:
  - Remove objects from edge caches before TTL expires.
  - Cost per invalidation (up to 3000 free per month).
  - Use versioned URLs for frequent updates (avoids invalidation cost).

TTL: min = 0s (dynamic content), default = 86400s (1 day), max = 31536000s (1 year).
```

### Lambda@Edge vs CloudFront Functions

| Feature | Lambda@Edge | CloudFront Functions |
|:--------|:-----------:|:-------------------:|
| **Runtime** | Node.js, Python | JavaScript only |
| **Max execution** | 5s (viewer), 30s (origin) | 1ms (50µs typical) |
| **Memory** | Up to 10GB | 2MB code size |
| **Triggers** | Viewer request/response, origin request/response | Viewer request/response only |
| **Use case** | Complex auth, origin rewrite | URL rewrites, header transforms, redirects |

---

## Cross-Links

- [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] for S3 + CloudFront OAC
- [[CICD/AWS/02_Core/03_ALB_NLB_and_Target_Groups]] for ALB as CloudFront origin
- [[CICD/AWS/04_Playbooks/04_Debug_S3_and_CloudFront]] for troubleshooting CloudFront issues
- [[CICD/AWS/05_Projects/03_Multi_Region_Active_Passive]] for Route 53 failover + CloudFront
