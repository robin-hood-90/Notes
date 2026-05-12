---
tags: [harness, playbook, delegate, connectivity, crash-oom, selector, token, proxy, logs]
aliases: ["Delegate Troubleshooting", "Delegate Not Connecting"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot Delegates

> [!summary] Goal
> Diagnose and fix delegate issues: delegate not connecting to Harness, task timeouts, OOM crashes, selector mismatches, token expiry, and proxy problems.

| Symptom | Likely cause | Diagnosis | Fix |
|:--------|:-------------|:----------|:----|
| Delegate shows `Disconnected` | Network (firewall, no DNS) | `kubectl logs <pod>` — "Failed to connect to app.harness.io:443" | Check egress, add proxy if needed |
| Delegate shows `Yet to connect` | Token invalid or wrong account ID | Check `DELEGATE_TOKEN` secret and `ACCOUNT_ID` | Regenerate delegate token, re-apply YAML |
| Tasks time out (no matching delegate) | Selector mismatch | `kubectl logs` — "no running delegate matches task" | Check `DELEGATE_TAGS` vs connector selectors |
| Delegate repeatedly crashes (OOMKilled) | Heap too small | `kubectl describe pod` — "OOMKilled" | Increase `-Xmx` in `JAVA_OPTS` |
| Delegate doesn't auto-upgrade | UPGRADER disabled | `DELEGATE_UPGRADER=false` being ignored | Check env value |

---

## Cross-Links

- [[CICD/Harness/01_Foundations/02_Delegates_Installation_Sizing_Operations]] for delegate setup
- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for selector setup
- [[CICD/Harness/04_Playbooks/02_Troubleshoot_Pipeline_Failures]] for related pipeline issues
