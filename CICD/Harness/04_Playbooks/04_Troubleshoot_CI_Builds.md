---
tags: [harness, playbook, ci, build, test-intelligence, cache, kaniko, dind, harness-cloud]
aliases: ["CI Build Troubleshooting", "Build Failure", "Test Intelligence Not Working"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot CI Builds

> [!summary] Goal
> Diagnose CI build failures: Harness Cloud capacity issues, build pod OOM, test intelligence (no impact detection), cache miss, DinD not running, Kaniko build error, and stage-level resources.

| Error | Likely cause | Check | Fix |
|:------|:-------------|:------|:-----|
| Build pod `OOMKilled` | Memory limit too low | Stage resources `memory: "2Gi"` | Increase to `3Gi` or `4Gi` |
| Test Intelligence empty (`0 tests`) | Language/framework not recognized | Check `language:` field in step | Set `language: Java`, `buildTool: Maven` |
| Cache miss every build | Cache key always changes | `key: cache-<+pipeline.sequenceId>` | Add fallback key: `cache-` (matches previous) |
| `Cannot connect to Docker daemon` | DinD not running | K8s build — no sidecar configured | Add `--privileged` to build pod or add DinD sidecar |
| Kaniko `destination not a valid registry` | No connection to ECR/GCR | Check K8s pod permissions for ECR/GCR | Add IRSA role or IAM keys to build infrastructure |
| `Cloud` infrastructure taking long | Harness Cloud capacity reached | Check region capacity | Switch to K8s cluster or different region |

---

## Cross-Links

- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI setup
- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for connector setup
- [[CICD/Harness/04_Playbooks/01_Troubleshoot_Delegates]] for delegate issues
