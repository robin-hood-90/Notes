---
tags: [harness, core, ecs, serverless, ssh, lambda, winrm, custom-deployment, rolling-update, blue-green]
aliases: ["Harness ECS CD", "Harness Serverless CD", "Harness SSH CD", "ECS Blue Green", "Serverless Lambda Deploy"]
status: stable
updated: 2026-05-11
---

# CD — ECS, Serverless, and SSH Deployments

> [!summary] Goal
> Master Harness CD for non-K8s targets: ECS (rolling/blue-green with CodeDeploy), Serverless Lambda (Serverless framework with stage variables, canary), and SSH/WinRM (command-based rolling updates on VMs). Custom deployment stages for any arbitrary orchestration.

## Table of Contents

1. [ECS Deployments (Rolling and Blue/Green)](#ecs-deployments)
2. [Serverless Framework Deployments](#serverless-framework-deployments)
3. [SSH and WinRM Deployments](#ssh-and-winrm-deployments)

---

## ECS Deployments (Rolling and Blue/Green)

> [!info] ECS deployments
> Harness deploys to ECS (Fargate or EC2) using task definitions. Services can be updated via **rolling** (gradually replace tasks) or **blue/green** (via CodeDeploy — new task set with test listener, then swap target groups).

### ECS Rolling deployment

```yaml
- step:
    type: EcsRollingDeploy
    name: "Rolling ECS Deploy"
    spec:
      sameAsAlreadyRunningInstances: false
      skipDryRun: true

service:
  serviceDefinition:
    type: ECS
    spec:
      manifests:
        - manifest:
            type: EcsTaskDefinition
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/ecs-configs"
                  files:
                    - "task-definitions/app.json"
        - manifest:
            type: EcsServiceDefinition
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/ecs-configs"
                  files:
                    - "services/app.json"
```

### ECS Blue/Green (CodeDeploy)

```yaml
- stage:
    type: Deployment
    spec:
      deploymentType: ECS
      execution:
        steps:
          - step:
              type: EcsBlueGreenCreateService
              name: "Create Green Service"
          - step:
              type: EcsBlueGreenSwapTargetGroups
              name: "Route to Green"
          - step:
              type: EcsBlueGreenDeleteService
              name: "Delete Blue"
```

---

## Serverless Framework Deployments

> [!info] Serverless deployments
> Harness deploys Serverless Framework applications via steps: `serverless deploy` and `serverless remove`. The `serverless.yml` is stored in Git.

```yaml
service:
  serviceDefinition:
    type: Serverless
    spec:
      manifests:
        - manifest:
            type: ServerlessAwsLambda
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "my-org/serverless-apps"
                  files:
                    - "payment-service/serverless.yml"
steps:
  - step:
      type: ServerlessAwsLambdaDeploy
      name: "Deploy Serverless"
  - step:
      type: ServerlessAwsLambdaRollback
      name: "Rollback Serverless"
```

---

## SSH and WinRM Deployments

> [!info] SSH/WinRM deployments
> For non-containerized apps (VMs, bare metal), Harness deploys via SSH or WinRM by copying artifacts and executing commands. Supports rolling updates across host arrays.

```yaml
infrastructureDefinition:
  type: Ssh
  spec:
    connectorRef: account.ssh_connector
    hostArray: "web-servers"

- step:
    type: Command
    name: "Copy Artifacts"
    spec:
      destinationPath: "/opt/app/releases"
      sourceType: "Artifact"
- step:
    type: RollingDeploy
    name: "Rolling SSH Update"
```

---

## Cross-Links

- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for K8s deployment patterns
- [[CICD/Harness/02_Core/03_CD_GitOps_ArgoCD_as_Harness]] for GitOps alternative
- [[CICD/Harness/01_Foundations/05_Services_Environments_and_Overrides]] for environment definitions
- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
