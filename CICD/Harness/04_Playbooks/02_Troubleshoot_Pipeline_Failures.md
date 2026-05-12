---
tags: [harness, playbook, pipeline, failure, timeout, rbac, secret, manifest, approval, log]
aliases: ["Pipeline Troubleshooting", "Pipeline Execution Failure"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot Pipeline Failures

> [!summary] Goal
> Diagnose and fix pipeline execution failures: connector test failures, pipeline timeouts, RBAC errors (user/role permissions), secret not found, manifest rendering errors, approval timeouts, and YAML expression resolution.

| Error | Cause | Check | Fix |
|:------|:------|:------|:----|
| `Connector test failed` | Delegate can't reach endpoint | Delegate logs (`Failed to dial`) | Verify network, firewall, proxy config |
| `Execution timed out` | Stage/step timeout too low | Stage timeout `10m` not enough | Increase `timeout: 30m` in step |
| `You do not have permission` | RBAC missing pipeline execute | User group → Role Binding for the pipeline resource | Add Pipeline Executor role for the target pipeline |
| `Secret not found` | Wrong scope | Pipeline references `<+account.secrets>`, but secret is project-level | Change expression or scope the secret to account |
| `Failed to render manifest` | Helm chart template error | Run `helm template` locally with same values | Fix chart syntax |
| `Approval took too long` | 24h default timeout | Approval stage timeouts after 24h not approve | Manually check, approve or reject |

---

## Cross-Links

- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for template errors
- [[CICD/Harness/04_Playbooks/01_Troubleshoot_Delegates]] for delegate issues
