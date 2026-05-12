---
tags: [harness, core, chaos-engineering, experiment, fault, probe, steady-state, resilience, k8s-faults, aws-faults]
aliases: ["Harness Chaos Engineering", "Chaos Experiment", "Chaos Fault Library", "Resilience Probe", "Steady State Hypothesis"]
status: stable
updated: 2026-05-11
---

# Chaos Engineering — Creating and Running Experiments

> [!summary] Goal
> Master Harness Chaos Engineering (HCE): chaos hubs (fault libraries), experiments (steady-state hypothesis → fault → probe — rollback condition), probes (HTTP, cmd, K8s, Prometheus), resilience score, fault categories (K8s, AWS, GCP, Azure), and integrating chaos in CD pipelines (deploy → verify with chaos → promote).

## Table of Contents

1. [Chaos Hubs and Fault Library](#chaos-hubs-and-fault-library)
2. [Chaos Experiments — Faults, Probes, and Steady-State](#chaos-experiments-faults-probes-and-steady-state)
3. [Chaos in CD Pipelines](#chaos-in-cd-pipelines)

---

## Chaos Hubs and Fault Library

> [!info] Chaos Hubs
> A Chaos Hub contains fault YAML templates. Harness provides a **Public Chaos Hub** with 100+ fault types. You can create custom faults in private hubs. Faults are organized by target: K8s, AWS, GCP, Azure, Linux, HTTP.

### Fault categories

| Category | Fault examples |
|:---------|:---------------|
| **K8s Pod** | `pod-delete`, `pod-cpu-hog`, `pod-memory-hog`, `pod-network-loss`, `pod-network-latency`, `container-kill` |
| **K8s Node** | `node-cpu-hog`, `node-memory-hog`, `node-restart` |
| **K8s Network** | `network-loss`, `network-latency`, `network-duplication`, `network-corruption`, `network-dns-error` |
| **K8s Volume** | `ebs-loss`, `node-storage-hog`, `disk-fill` |
| **AWS** | `ec2-stop`, `ec2-restart`, `ebs-volume-loss`, `asg-instance-terminate` |
| **GCP** | `gcp-vm-instance-stop`, `gcp-vm-instance-restart` |
| **Azure** | `azure-vm-instance-stop`, `azure-vm-instance-restart` |
| **HTTP** | `http-latency`, `http-abort`, `http-modify-request`, `http-modify-response` |

```yaml
# Pod delete fault (from public hub):
kind: ChaosEngine
apiVersion: litmuschaos.io/v1alpha1
spec:
  engineState: "active"
  appinfo:
    appns: "payment-prod"
    applabel: "app.kubernetes.io/name=payment-service"
    appkind: "deployment"
  chaosServiceAccount: "harness-chaos-sa"
  experiments:
    - name: pod-delete
      spec:
        rank: 1
        probe:
          - name: "check-service"
            type: httpProbe
            httpProbe/inputs:
              url: "http://payment-service.payment-prod:8080/healthz"
              expectedResponseCode: "200"
```

---

## Chaos Experiments — Faults, Probes, and Steady-State

> [!info] Experiment
> A chaos experiment defines: **steady-state hypothesis** (the system must remain healthy), **fault** (what goes wrong), **probes** (how we verify health during/after the fault), and a **rollback condition** (if probes fail, abort experiment and trigger rollback in CD pipeline).

### Experiment structure

```yaml
# Harness Chaos Experiment YAML:
experiment:
  name: "payment-pod-delete"
  identifier: payment_pod_delete
  environment: production
  steps:
    - steadyStateHypothesis:
        name: "Service must be healthy"
        probes:
          - probe:
              name: "http-check"
              type: http
              spec:
                url: "http://payment-service.prod:8080/health"
                expectedResponse: "{ \"status\": \"healthy\" }"
                retries: 3
    - fault:
        name: "Kill Payment Pod"
        type: K8sPodDelete
        spec:
          namespace: payment-prod
          targetPods: 1
          duration: 30s              # Kill one pod for 30 seconds
    - probe:
        name: "Verify Payment API"
        type: http
        spec:
          url: "http://payment-service.prod:8080/api/health"
          assertion: "<+httpResponseCode> == 200"
      # If probe fails → experiment fail → pipeline app can roll back
```

### Probes

```yaml
# HTTP probe (check an endpoint):
- probe:
    name: "api-health"
    type: http
    spec:
      url: "http://payment-service:8080/health"
      method: GET
      assertion: "<+responseBody> == \"ok\""
      retries: 5

# Cmd probe (run a command inside container):
- probe:
    name: "db-connectivity"
    type: cmd
    spec:
      command: "pg_isready -h postgres -U app"
      timeout: 10s

# K8s probe (check resource status):
- probe:
    name: "pod-status"
    type: k8s
    spec:
      group: "apps"
      version: "v1"
      resource: "deployment"
      name: "payment-service"
      namespace: "payment-prod"
      assertion: "<+status.readyReplicas> == <+status.replicas>"

# Prometheus probe (check metric):
- probe:
    name: "request-latency"
    type: prometheus
    spec:
      prometheusConnector: account.prometheus
      query: "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"
      assertion: "<+value> < 0.5"          # p99 < 500ms
```

---

## Chaos in CD Pipelines

```yaml
# Run chaos experiment as a step in a CD pipeline:
- stage:
    type: Deployment
    spec:
      execution:
        steps:
          - step:
              type: K8sRollingDeploy
              name: "Deploy to Staging"
          - step:
              type: Chaos
              name: "Verify Resilience"
              spec:
                experimentRef: payment_pod_delete
          - step:
              type: HarnessApproval
              name: "Manual Promote to Prod"
              spec:
                approvers:
                  userGroups:
                    - account._account_all_users
                  minimumCount: 1
```

---

## Cross-Links

- [[CICD/Harness/02_Core/06_Chaos_Engineering]] for this module
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for chaos in full CD pipeline
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for K8s deployment + chaos
- [[CICD/Harness/03_Advanced/02_SRM_SLOs_Error_Tracking_and_Change_Intelligence]] for SLO + chaos impact measurement
