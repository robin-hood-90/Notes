---
tags: [aws, foundations, api-gateway, rest, http, websocket, stages, throttling, authorizer, cognito, caching]
aliases: ["API Gateway Deep Dive", "API Gateway REST", "API Gateway HTTP", "API Gateway WebSocket"]
status: stable
updated: 2026-05-11
---

# API Gateway — REST, HTTP, and WebSocket APIs

> [!summary] Goal
> Master API Gateway: REST vs HTTP vs WebSocket APIs, stages and deployments, usage plans and API keys, throttling, request/response transformation, authorizers (Cognito, Lambda, IAM), CORS, canary deployments, custom domains, WAF integration, and caching.

## Table of Contents

1. [API Types](#api-types)
2. [Stages, Usage Plans, and Throttling](#stages-usage-plans-and-throttling)
3. [Authorizers](#authorizers)
4. [Canary Deployments and Caching](#canary-deployments-and-caching)

---

## API Types

> [!info] API Gateway
> API Gateway creates, publishes, maintains, monitors, and secures APIs at any scale. Three types: **REST** (full feature set, VTL transformations, usage plans), **HTTP** (lower cost, faster, proxy-only), **WebSocket** (bidirectional, real-time communication).

| Feature | REST API | HTTP API | WebSocket API |
|:--------|:--------:|:--------:|:-------------:|
| **Request transform** | Yes (VTL mapping templates) | No | N/A |
| **Usage plans & API keys** | Yes | Yes | N/A |
| **WAF** | Yes | Yes | Limited |
| **Custom domain** | Yes | Yes | Yes |
| **Private (VPC)** | Yes | No | No |
| **Canary deployments** | Yes | No | No |
| **Cost** | Higher | Lower (~70% cheaper) | Per connection + messages |
| **Lambda authorizer** | Yes | Yes | Yes |
| **Cognito authorizer** | Yes | Yes | Yes |

### REST API features

```text
Mapping templates (VTL — Velocity Template Language):
  - Transform request/response payloads (e.g., convert JSON → XML).
  - Access: $input.params('param'), $input.json('$'), $input.path('$'), $util.escapeJavaScript().
  - Can invoke before the integration (request) and after the integration (response).
  - Useful for: SOAP backend, legacy XML integrations.

Integration types:
  - Lambda: API Gateway invokes a Lambda function.
  - HTTP: proxy to any HTTP endpoint.
  - AWS Service: API Gateway directly calls an AWS service (e.g., DynamoDB, SQS, Step Functions).
  - Mock: return a response without calling a backend (for testing).
  - VPC Link: connect to a Network Load Balancer in a VPC (for private backend).
```

---

## Stages, Usage Plans, and Throttling

> [!info] Stages
> Stages represent the API lifecycle: dev, staging, prod. Each stage has its own URL, settings, and canary. Stage variables allow per-stage configuration (Lambda function alias, endpoint URL).

```text
Stage variables:
  - Environment-specific values (Lambda function alias, endpoint URL).
  - Use: dev → alias:dev, prod → alias:prod.
  - Supported in: Lambda integration ARN, HTTP URL, mapping templates.

Usage plans + API keys:
  - API keys: per-customer or per-application identifier.
  - Usage plan: throttling (rate + burst per second) and quota (daily/monthly limit).
  - Use with: REST or HTTP APIs (need API key required = true on method).

Throttling:
  - Account-level: 10,000 requests per second (default) with 5,000 burst.
  - Per-method: override for specific routes.
  - Rate limit headers returned: X-RateLimit-Limit, X-RateLimit-Remaining.
  - HTTP 429: Too Many Requests (when throttled).
```

---

## Authorizers

| Authorizer type | How it works | Use case |
|:----------------|:-------------|:---------|
| **Lambda** | Call a Lambda function with the token/request → Lambda returns IAM policy | Custom JWT validation, custom auth logic |
| **Cognito** | Verify JWT token from Cognito User Pool (OAuth 2.0 / OIDC) | User authentication with Cognito |
| **IAM** | Sign API request with AWS Signature V4 (IAM credentials) | Service-to-service, cross-account access |

### REST API Lambda authorizer

```text
Request flow:
  1. Client sends request with token (Authorization header).
  2. API Gateway calls authorizer Lambda with the token.
  3. Lambda validates the token (JWT, OAuth introspection, custom logic).
  4. Lambda returns IAM policy: Effect (Allow/Deny), Resource (ARN).
  5. API Gateway caches the policy for 5 minutes (default TTL).
  6. If allowed, API Gateway sends the original request to the backend.

Caching: reduce Lambda invocations by caching the auth decision.
  - TTL: 0s (don't cache) to 3600s (1 hour). Default: 300s.
  - Use identity sources (header, query string, stage variable) to build the cache key.
```

---

## Canary Deployments and Caching

### Canary deployments

```text
Canary: a percentage of traffic is routed to a new version of the API.

  Production stage → version 1 (100% traffic)
  Create canary → version 2 (5% traffic)
  If no errors after N minutes, promote canary to 100%.
  If errors, delete canary (rollback to 100% version 1).

CloudWatch metrics per stage + per canary (5XX, 4XX, latency).
```

### API caching

```text
API Gateway caches responses to reduce backend load and improve latency.
  - Cache size: 500MB – 237GB.
  - TTL: 0s (no caching) to 3600s. Default: 300s.
  - Encryption: optional encryption at rest.
  - Per-key: cache by parameters, headers, or stage variable.
  - Invalidation: flush entire cache (or individual entries with `Cache-Control: max-age=0`).

Cost: cache instances are billed per hour regardless of usage.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/07_Lambda_Functions_Events_and_Best_Practices]] for Lambda + API Gateway
- [[CICD/AWS/02_Core/03_ALB_NLB_and_Target_Groups]] for ALB vs API Gateway
- [[CICD/AWS/02_Core/08_WAF_Shield_and_Network_Security]] for WAF on API Gateway
- [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] for full serverless
