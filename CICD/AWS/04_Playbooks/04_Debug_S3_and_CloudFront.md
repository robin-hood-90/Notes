---
tags: [aws, playbook, s3, cloudfront, access-denied, cors, presigned-url, cache-invalidation, origin-failover]
aliases: ["Debug S3 Access", "Debug CloudFront Issues", "CloudFront Troubleshooting"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug S3 and CloudFront

> [!summary] Goal
> Diagnose S3 access issues (bucket policy vs IAM vs ACL), CORS errors, presigned URL expiration, CloudFront cache invalidation failures, origin connectivity, signed URL format problems, and OAC misconfiguration.

## S3 Access Issues

| Symptom | Likely cause | Check |
|:--------|:-------------|:------|
| `AccessDenied` for GET | S3 bucket policy or IAM | Policy simulator, `Principal` match, `Resource` exact |
| `AccessDenied` for cross-account | Bucket policy not granted | Check `Principal.Account` in bucket policy |
| `CORS` error in browser | Missing CORS headers | Check bucket CORS config (`AllowedOrigin`, `AllowedMethods`) |
| `403` for presigned URL | URL expired or signed with different credentials | Check `Expires` timestamp, signer IAM permissions |

---

## Cross-Links

- [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] for S3 policies
- [[CICD/AWS/01_Foundations/08_Route53_and_CloudFront]] for CloudFront configuration
- [[CICD/AWS/05_Projects/02_Serverless_API_with_Lambda_API_Gateway_DynamoDB]] for CloudFront + API Gateway
