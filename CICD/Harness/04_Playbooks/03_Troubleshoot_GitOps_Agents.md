---
tags: [harness, playbook, gitops, agent, sync, pr, image-updater, out-of-sync, application]
aliases: ["GitOps Troubleshooting", "ArgoCD Agent Issues", "Sync Failure"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot GitOps Agents

> [!summary] Goal
> Diagnose GitOps agent issues: agent not connected, sync failure (ComparisonError, Missing, Extra resources, OutOfSync), image updater not creating PRs, engine OOM, and authentication failures.

| Symptom | Likely cause | Check | Fix |
|:--------|:-------------|:------|:-----|
| Agent `Disconnected` | WebSocket dropped | Agent logs `connection lost` | Check Harness SaaS outbound access on port 443 (WebSocket) |
| Sync `ComparisonError` | Invalid YAML in Git | View app diff in ArgoCD UI | Fix malformed YAML in Git repo |
| App shows `OutOfSync` | Manual change on cluster | `argocd app diff <app>` | `selfHeal: true` in sync policy, or manually sync |
| App shows `Missing` | Resource exists in Git but not on cluster | Check sync policy `prune: true` | Enable automated prune |
| App shows `Extra` | Resource exists on cluster but not in Git | Resource created by another tool | Remove resource from cluster or add to Git |
| Image updater not creating PR | `tagRegex` not matching new image | Check ECR for correct image tag | Update tagRegex to match tag pattern |

---

## Cross-Links

- [[CICD/Harness/02_Core/03_CD_GitOps_ArgoCD_as_Harness]] for GitOps setup
- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for Git Experience
- [[CICD/Harness/05_Projects/02_GitOps_PR_Pipeline_with_Image_Updater]] for GitOps project
