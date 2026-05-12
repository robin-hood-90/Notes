---
tags: [kubernetes, k8s, cicd, playbook, crashloopbackoff, pod, troubleshoot, exit-code, oom, probe]
aliases: ["CrashLoopBackOff Playbook", "Pod Troubleshooting", "Container Crash Debugging"]
status: stable
updated: 2026-05-11
---

# Playbook: Troubleshoot CrashLoopBackOff

> [!summary] Goal
> Diagnose and fix containers that keep restarting. Step-by-step triage from pod state to root cause: image errors, config issues (ConfigMap/Secret missing), probe failures, OOMKilled, resource limits, PVC pending, and node pressure.

## Table of Contents

1. [Quick Triage Flow](#quick-triage-flow)
2. [Common CrashLoopBackOff Causes](#common-crashloopbackoff-causes)
3. [Exit Code Reference](#exit-code-reference)

---

## Quick Triage Flow

```bash
# 1. Check pod status
kubectl get pods -n <namespace>
kubectl describe pod <pod-name>   # Look for Events section

# 2. Check container logs (last attempt)
kubectl logs <pod-name> --previous   # Logs from PREVIOUS (crashed) container

# 3. Check if pod is OOMKilled
kubectl describe pod <pod-name> | grep -i "exit\|OOM\|killed"

# 4. Check all conditions
kubectl get pod <pod-name> -o yaml | grep -A5 "containerStatuses:"

# 5. Ephemeral debug container (K8s 1.25+)
kubectl debug <pod-name> -it --image=busybox --target=<container>
```

---

## Common CrashLoopBackOff Causes

| Cause | Symptom | Diagnosis | Fix |
|:------|:--------|:----------|:----|
| **Image pull error** | Pod stuck in `ImagePullBackOff` | `kubectl describe pod` → event: `Failed to pull image "nginx:invalid": not found` | Fix image tag/name, check registry credentials |
| **ConfigMap/Secret missing** | Container exits with 1, no start | `kubectl logs` → error reading config file | Check CM/Secret exists in the same namespace (`kubectl get cm`) |
| **Liveness probe failure** | Container exits >137, restart | `kubectl describe pod` → `Liveness probe failed` | Tune probe path/port/initialDelay/period; `ReadinessProbe` maybe failed first causing no traffic + liveness restarts |
| **OOMKilled** | Exit code 137 | `kubectl describe pod` → `OOMKilled: true`; `dmesg | grep -i killed` | Increase memory limit, fix memory leak |
| **Resource limits too low** | Container killed silently | Exit 137 with no OOM in events, CPU throttle detected via metrics | Increase CPU/memory limits, use VPA recommendations |
| **PVC not bound** | Pod stuck in `Pending` | `kubectl describe pod` → `persistentvolumeclaim "pvc-name" not found` | Check PVC exists, StorageClass exists, PV provisioner running |
| **Node pressure (disk/memory)** | Pod evicted | `kubectl describe pod` → `Node was out of disk space` | Free node resources, add nodes, set pod priority |
| **Application initialization error** | Container exits with 1 (but no probe/OOM) | `kubectl logs --previous` → application error from the last run | Fix application code/config |
| **TLS/cert errors** | Container unable to start web server | Logs show `certificate has expired` or `failed to load certificate` | Regenerate certs, restart pods |
| **MutatingWebhook failure** | Pod stuck `Pending`, no events | `kubectl get pod` → no status; webhook misconfiguration causing pod creation to time out | Check webhook controller, service, cert, disable webhook temporarily for test |

---

## Exit Code Reference

| Code | Meaning | Common cause | Check |
|:----:|:--------|:-------------|:------|
| **0** | Success | Normal exit (Job completed) | Not an error — job finished |
| **1** | Application error | Config error, runtime exception, panic | `kubectl logs --previous` |
| **126** | Permission error | Command can't execute | Check binary permissions, command path |
| **127** | Command not found | Entrypoint binary missing in image | Check image contents (docker run --entrypoint) |
| **130** | SIGINT | Process killed with Ctrl+C | Normal signal; check sent SIGTERM behavior? |
| **137** | SIGKILL (OOM) | Process killed by kernel OOM killer | Increase memory limit, fix memory leak; check `OOMKilled: true` in describe |
| **139** | SIGSEGV | Segmentation fault (segfault) | Memory corruption, bad pointer, incompatible lib, language runtime bug |
| **143** | SIGTERM | Graceful shutdown | Normal for `kubectl delete` or scale down — check pod lifecycle |
| **255** | Unknown error | Generic exit (most languages use 1) | See code 1 |

### Probe tuning parameters

```yaml
# Initial delay: give app time to start before probing.
# Period: how often to probe (default 10s).
# Failure threshold: number of failures before restart (default 3).

livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10     # Wait 10s before first probe — adjust if app startup is slow
  periodSeconds: 10            # Check every 10s
  failureThreshold: 6          # 6 failures * 10s = 60s tolerance for transient errors
  timeoutSeconds: 3            # Probe must respond within 3s

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5

startupProbe:                  # K8s 1.18+ — for slow-starting apps
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 1
  periodSeconds: 2
  failureThreshold: 30         # 60 seconds to start before liveness takes over
```

### Ephemeral debug containers

```bash
# Add debugging tools to a running (or crash-looping) pod:
kubectl debug <pod-name> -it --image=nicolaka/netshoot --target=<container-name>

# This starts a new container in the pod's namespaces:
# - Same network namespace (localhost works)
# - Same IPC namespace
# - Same PID namespace (--target)
# - Attach/detach with ^P^Q

# Common debugging commands in netshoot:
#   curl localhost:8080/healthz
#   dig service.namespace.svc.cluster.local
#   nslookup <hostname>
#   tcpdump port 8080
#   nsenter -t 1 -m -u -n -i sh   # Enter the container's mount namespace
```

---

## Cross-Links

- [[CICD/Kubernetes/02_Core/04_Debugging_with_kubectl]] for general kubectl debugging
- [[CICD/Kubernetes/02_Core/03_HealthChecks_Resources_and_HPA]] for probe configuration deep dive
- [[CICD/Kubernetes/03_Advanced/01_Resource_Requests_Limits_and_QoS_Deep_Dive]] for QoS and OOM analysis
- [[CICD/Kubernetes/05_Projects/01_Deploy_a_Service_With_HPA_and_Ingress]] for full deployment health
