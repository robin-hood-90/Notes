---
tags: [cicd, secrets, security, oidc, vault, rotation, scanning]
aliases: ["Secrets Management", "Secret Rotation", "OIDC", "Secret Scanning", "TruffleHog", "Secret Injection"]
status: stable
updated: 2026-05-11
---

# Secrets Management

> [!summary] Goal
> Prevent credential leaks while enabling automation. Prefer short-lived credentials, OIDC federation over access keys, secret scanning in CI/CD, and secure injection patterns (env vars, volume mounts, sidecar).

## Table of Contents

1. [Secret Types and Classification](#secret-types-and-classification)
2. [Authentication: OIDC vs Access Keys](#authentication-oidc-vs-access-keys)
3. [Secrets in CI/CD](#secrets-in-ci-cd)
4. [Secret Scanning and Incident Response](#secret-scanning-and-incident-response)

---

## Secret Types and Classification

> [!info] Secret
> Any credential that grants access to a system, data, or API. Secrets must be stored encrypted, rotated regularly, and never logged or committed. Classification determines rotation urgency and access controls.

| Secret type | Examples | Rotation frequency | Storage | Risk if leaked |
|:------------|:---------|:------------------:|:--------|:--------------:|
| **Environment variable** | DB password, API key, service account key | 90 days / on rotation | Secret manager / CI store | Medium |
| **Token** | GitHub PAT, GitHub App token, Slack token, JWT signing key | 30 days / ephemeral | Secret manager / OIDC | High (immediate rotate) |
| **Certificate** | TLS cert, mTLS client cert, SSH key | Per cert lifecycle (30-365 days) | ACM, cert-manager, Vault PKI | Medium-High |
| **Cloud credential** | AWS access key, GCP service account | Short-lived (STS) or 90 days | OIDC preferred, fallback to secret manager | Critical |
| **Signing key** | Cosign key, GPG key, code signing cert | 90 days / per rotation | HSM or KMS, never in CI store | Critical (supply chain) |

---

## Authentication: OIDC vs Access Keys

> [!info] OIDC
> OpenID Connect allows CI/CD systems (GitHub Actions, GitLab CI, CircleCI) to authenticate to cloud providers WITHOUT storing long-lived access keys. The CI runner presents a JWT token signed by the CI system; the cloud provider exchanges it for temporary credentials (STS).

| Method | Credential lifetime | Rotation | Audit | Setup complexity | Best for |
|:-------|:------------------:|:--------:|:----:|:----------------:|:---------|
| **OIDC (recommended)** | Short (1h) | Automatic (per run) | Full (each CI run is logged) | Medium (OIDC provider + trust policy) | All new CI/CD pipelines |
| **Access keys** | Long (months-years) | Manual | Partial (key used, not per-run) | Low | Legacy systems, non-OIDC providers |
| **Service account token** | Medium (days-months) | Manual/automated | Depends on system | Low-Medium | K8s-native, GCP |
| **Vault** | Short (lease) | Automatic | Full | High | Multi-cloud, legacy infra |

```yaml
# OIDC setup — GitHub Actions → AWS:
# IAM OIDC provider:
provider_url: https://token.actions.githubusercontent.com
client_id_list: ["sts.amazonaws.com"]

# IAM role trust policy:
{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/..." },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike": { "token.actions.githubusercontent.com:sub": "repo:org/repo:ref:refs/heads/main" }
    }
}
```

---

## Secrets in CI/CD

> [!info] Secret injection
> Secrets enter CI/CD through environment variables, volume-mounted files, or sidecar containers. The key rule: secrets are NEVER part of the build artifact (no baked-in passwords, no build-arg secrets leaking to image layers).

### Injection patterns

| Pattern | How it works | Security | Complexity | Use case |
|:--------|:-------------|:--------:|:----------:|----------|
| **CI environment variable** | CI platform provides secret store (GitHub Actions secrets, GitLab variables) | Medium (CI store encrypted, but visible in logs if misconfigured) | Low | Simple, single-platform |
| **Cloud secret manager** | Fetch at runtime from AWS Secrets Manager, GCP Secret Manager, Azure Key Vault | High (IAM-protected, audited) | Medium | Multi-cloud, large orgs |
| **Vault sidecar** | Vault agent runs alongside app, fetches secrets and writes to shared volume | High (lease-based, auto-rotated) | High | Enterprise, dynamic secrets |
| **K8s Secret** | Mounted as volume or env var, encrypted with KMS | Medium (RBAC + encryption) | Low-Medium | K8s-native workloads |
| **External Secrets Operator** | Syncs from AWS/GCP/Azure/Vault to K8s Secret | High | Medium | K8s + external vault |

```text
Don't:
  - Bake secrets into container images (Docker build args leak in image history).
  - Print environment variables on failure (CI logs may contain the value).
  - Share one credential across environments (dev leak → prod compromised).
  - Commit .env files or secret files to Git (use git-secrets or pre-commit hooks).

Do:
  - Use OIDC for cloud provider authentication.
  - Use short-lived credentials where possible.
  - Scan for secrets in every commit (CI-integrated secret scanning).
  - Rotate secrets immediately on suspected exposure.
```

---

## Secret Scanning and Incident Response

> [!info] Secret scanning
> Secret scanning detects accidentally committed credentials before they reach production. Tools scan commit history for API key patterns, JWT tokens, AWS access keys, etc.

### Tools comparison

| Tool | Scan scope | CI integration | False positives | Key features |
|:-----|:-----------|:--------------:|:---------------:|:-------------|
| **GitHub secret scanning** | Public repos (free), private (paid) | Native (GitHub) | Low | Auto-revoke for known patterns |
| **truffleHog** | Git history, files, S3 | GitHub Actions, pre-commit | Medium | Entropy + regex, deep history |
| **Gitleaks** | Git history, files | GitHub Actions, pre-commit, Docker | Low-Medium | High accuracy, SARIF output |
| **git-secrets** | Git commits (hook) | Pre-commit only | Low | Simple pattern matching |
| **ggshield** (GitGuardian) | Git history, CI | GitHub Actions, GitLab CI | Very low | Broadest pattern library |

```yaml
# Gitleaks in GitHub Actions:
name: Secret Scanning
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

```text
Secret leak response:
  1. Detect leak (secret scanning alert, CI failure, report).
  2. Rotate credential immediately (AWS access key, GitHub token, DB password).
  3. Remove secret from Git history (BFG Repo-Cleaner for old commits, git filter-repo for recent).
  4. Audit logs for unauthorized access using the leaked credential.
  5. Add secret scanning to prevent recurrence.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for IAM and OIDC setup
- [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] for AWS Secrets Manager
- [[CICD/Harness/01_Foundations/04_Secrets_Managers_SSH_Keys_Files]] for Harness secrets
- [[CICD/GitHubActions/02_Core/01_Secrets_Environments_and_OIDC]] for GitHub Actions OIDC
- [[CICD/Kubernetes/01_Foundations/03_ConfigMaps_Secrets_and_Volumes]] for K8s secrets
