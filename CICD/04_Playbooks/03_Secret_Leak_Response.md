---
tags: [cicd, playbook, security, secret-leak, rotate, audit, git-history, scanning]
aliases: ["Secret Leak Response", "Credential Exposure", "Git History Cleanup"]
status: stable
updated: 2026-05-11
---

# Playbook: Secret Leak Response

> [!summary] Goal
> Revoke/rotate credentials quickly and eliminate the leak source. Follow: treat as compromised → rotate → remove from history → scan for tracing.

## 1. Treat as Compromised

Assume the secret is public. Do NOT assume Git commit history is private. Even if the commit is old, secrets scanning tools cache leaked credentials.

| Detection source | Action |
|:-----------------|:-------|
| GitHub secret scanning alert | Rotate immediately (GitHub may auto-revoke known patterns) |
| CI log contains the secret | Rotate, then find the log line that leaked it and fix code/CI |
| Internal scanning (gitleaks/truffleHog) | Rotate, remove from Git history |
| Report from a security researcher | Rotate, audit usage, thank the reporter |
| External breach notification | Rotate, audit, report to security team |

## 2. Rotate

| Secret type | Rotate via | Verify |
|:------------|:-----------|:-------|
| AWS access key | IAM console → Deactivate → Create new → Update apps → Delete old | `aws sts get-caller-identity` with new key |
| GitHub PAT | Settings → Developer settings → Token → Regenerate | `curl -H "Authorization: Bearer <new_token>" https://api.github.com/user` |
| DB password | ALTER USER / AWS Secrets Manager rotation | `psql -h <host> -U <user>` with new password |
| API token (third-party) | Service provider's dashboard | API call with new token |
| SSH key | Generate new key pair → update `authorized_keys` / deploy key | `ssh -i <new_key> user@host` |
| TLS certificate | ACM / cert-manager re-issue | `openssl s_client -connect host:443` |

## 3. Remove from Git History

| Tool | Command | When to use |
|:-----|:--------|:------------|
| **BFG Repo-Cleaner** | `bfg --replace-text passwords.txt` | Remove a specific string from entire history (fastest) |
| **git filter-repo** | `git filter-repo --invert-paths --path path/to/file.env` | Remove a specific file from entire history |
| **git filter-branch** | (Avoid — slow and error-prone) | Only as last resort |
| **GitHub support** | Contact GitHub support for full history scrub | When the secret is cached in GitHub's own systems |

```bash
# BFG example (remove a file from history):
# 1. Create a file with the secret:
echo "AKIAIOSFODNN7EXAMPLE" > passwords.txt
# 2. Run BFG:
java -jar bfg.jar --replace-text passwords.txt my-repo.git
# 3. Force push:
git push --force --all
```

## 4. Prevent Recurrence

```text
  - Add secret scanning to CI (gitleaks, truffleHog on every push).
  - Use OIDC instead of access keys (no long-lived credentials).
  - Use secret manager references in code (not .env files).
  - Add pre-commit hook (git-secrets).
  - Rotate all credentials quarterly (scheduled rotation policy).
```

---

## Cross-Links

- [[CICD/02_Core/02_Secrets_Management]] for prevention strategies
- [[CICD/GitHubActions/02_Core/01_Secrets_Environments_and_OIDC]] for OIDC setup
- [[CICD/AWS/02_Core/06_KMS_and_Secrets_Manager]] for AWS Secrets Manager rotation
- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for IAM credential rotation
