---
tags: [harness, project, cd, pipeline, k8s, helm, Chaos, approval, rollback, blue-green]
aliases: ["Full CD Pipeline Project", "K8s Helm Chaos Approval Rollback"]
status: stable
updated: 2026-05-11
---

# Project: Full CD Pipeline with Approvals and Rollback

> [!summary] Goal
> Build a complete CD pipeline: K8s rolling deploy with Helm → verify with chaos experiment (pod-kill) → waiting approval → promote to production with rollback on failure. Includes: connectors, service, environment, pipeline with stages, and rollback configuration.

## Architecture

```text
[CI Stage (external)] → [Deploy to Staging → Helm Rolling] → [Chaos: pod-delete] → [HTTP Probe check] → [Manual Approval] → [Deploy to Prod → Blue/Green] → [Rollback if fails]
```

### Harness project

```yaml
# Project YAML:
project:
  name: "payment-service-cd"
  identifier: payment_service_cd
  orgIdentifier: platform-engineering
```

### Service definition

```yaml
service:
  name: "payment-service"
  identifier: payment_service
  serviceDefinition:
    type: Kubernetes
    spec:
      manifests:
        - manifest:
            type: HelmChart
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/helm-charts"
                  files:
                    - "payment/Chart.yaml"
              valuesPaths:
                - "payment/values/values.yaml"
                - "payment/values/env/<+pipeline.variables.environment>.yaml"
      artifacts:
        - primary:
            type: DockerRegistry
            spec:
              connectorRef: account.aws_ecr
              imagePath: "my-org/payment-service"
              tag: <+pipeline.variables.artifact_tag>
```

### Pipeline

```yaml
pipeline:
  name: "Payment Service CD Pipeline"
  identifier: payment_service_cd
  projectIdentifier: payment_service_cd
  orgIdentifier: platform-engineering
  variables:
    - name: environment
      type: String
      value: <+input>
    - name: artifact_tag
      type: String
      value: <+input>
  stages:
    - stage:
        name: "Deploy to Staging"
        type: Deployment
        spec:
          service: payment_service
          environment: staging
          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: account.staging_eks	_cluster
              namespace: payment-staging
              releaseName: "payment-<+pipeline.sequenceId>"
          execution:
            steps:
              - step:
                  type: K8sRollingDeploy
                  name: "Rolling Deploy Staging"
              - step:
                  type: Chaos
                  name: "Resilience: Pod Kill"
                  spec:
                    experimentRef: payment_pod_delete
              - step:
                  type: Http
                  name: "Verify Health"
                  spec:
                    url: "http://payment-service.staging/healthz"
                    method: GET
                    assertion: "<+httpResponseCode> == 200"
    - stage:
        name: "Approval"
        type: Approval
        spec:
          approval:
            type: HarnessApproval
            spec:
              approvers:
                userGroups:
                  - account._account_all_users
                minimumCount: 1
              approverInputs:
                - name: "prod_version"
                  defaultValue: "Rollback"  
    - stage:
        name: "Deploy to Prod"
        type: Deployment
        spec:
          service: payment_service
          environment: production
          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: account.prod_eks_cluster
              namespace: payment-prod
              releaseName: "payment-prod"
          execution:
            steps:
              - step:
                  type: K8sBlueGreenDeploy          
                 	name : "Blue-Green Deploy"
                  spec:
                    skipDryRun: true
              - step:
                  type: K8sBGServices
                  name: "Swap to Green"
              - step:
                  type: K8sBGStageScaleDown
                  name: "Cleanup Blue"
          rollbackSteps:
            - step:
                type: K8sBGServices
                name: "Swap Back to Blue"
```

---

## Cross-Links

- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for K8s deploy steps
- [[CICD/Harness/02_Core/06_Chaos_Engineering]] for chaos experiment steps
- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
- [[CICD/Harness/01_Foundations/05_Services_Environments_and_Overrides]] for service definitions
