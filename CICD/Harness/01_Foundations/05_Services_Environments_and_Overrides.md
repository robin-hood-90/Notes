---
tags: [harness, foundations, services, environments, manifests, artifacts, config-files, overrides, infrastructure]
aliases: ["Harness Services", "Harness Environments", "Service Overrides", "Infrastructure Definition", "Manifests", "Artifacts"]
status: stable
updated: 2026-05-11
---

# Services, Environments, and Overrides

> [!summary] Goal
> Master Harness services (manifests, artifacts, config files), environments (prod/staging/dev with overrides), infrastructure definitions (K8s cluster + namespace, ECS cluster + service), and environment scoping.

## Table of Contents

1. [Services — Manifests, Artifacts, and Config Files](#services-manifests-artifacts-and-config-files)
2. [Environments and Overrides](#environments-and-overrides)
3. [Infrastructure Definitions](#infrastructure-definitions)

---

## Services — Manifests, Artifacts, and Config Files

> [!info] Service
> A service represents a microservice or application. It defines what to deploy: **manifest** (K8s YAML, Helm chart, Kustomize, OpenShift template), **artifact** (Docker image, package, tarball), and **config files** (environment-specific properties). Services are reusable across environments and pipelines.

### Manifest sources

| Type | Source | Description |
|:-----|:-------|:------------|
| **K8s YAML** | Git repo | Direct YAML files (`deployment.yaml`, `service.yaml`) |
| **Helm** | Helm repo (HTTP/OCI), Git repo | Helm chart with `values.yaml` overrides |
| **Kustomize** | Git repo | Kustomize overlay (base + env overlay) |
| **OpenShift Template** | Git repo | OpenShift Template (`.yaml`) |
| **Docker + K8s YAML** | Git repo | Dockerfile from Git + K8s manifests from Git |
| **AWS ECS** | Git repo, S3, ECR | ECS task definition + service JSON |

### Service YAML

```yaml
# K8s service example (Harness YAML):
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
                  repoName: "helm-charts/payment-service"
                  files:
                    - "Chart.yaml"
                    - "templates/"
              valuesPaths:
                - "values/values.yaml"
      artifacts:
        - primary:
            type: DockerRegistry
            spec:
              connectorRef: account.aws_ecr
              imagePath: "my-org/payment-service"
              tag: <+input>          # Resolved at runtime or trigger
      configFiles:
        - configFile:
            type: Git
            spec:
              store:
                type: Github
                spec:
                  connectorRef: account.github_org
                  gitFetchType: Branch
                  repoName: "configs/payment-service"
                  paths:
                    - "config.yaml"
```

### Primary vs Sidecar artifacts

```yaml
# Primary artifact is the main application image.
# Sidecar artifacts are additional images (sidecar containers).
service:
  serviceDefinition:
    type: Kubernetes
    spec:
      artifacts:
        - primary:          # Main app container
            type: DockerRegistry
            spec:
              imagePath: "nginx"
              tag: "1.27"
        - sidecars:         # Additional containers
            - sidecar:
                identifier: "fluentbit"
                type: DockerRegistry
                spec:
                  imagePath: "fluent/fluent-bit"
                  tag: "3.0"
```

---

## Environments and Overrides

> [!info] Environment
> An environment groups infrastructure definitions (clusters, namespaces), service overrides, and config files. Environments represent deployment stages: dev → staging → prod. Each environment can have environment-level variables and secrets that override service defaults.

```yaml
# Environment YAML:
environment:
  name: "production"
  identifier: production
  type: Production          # Production or PreProduction
  variables:
    - name: "replicas"
      type: String
      value: "5"
    - name: "log_level"
      type: String
      value: "warn"
```

### Service override

```yaml
# Override service config for a specific environment (production):
serviceOverrides:
  environmentRef: production
  manifests:
    - manifest:
        type: HelmChart
        spec:
          valuesPaths:
            - "values/prod-values.yaml"
            - "values/global.yaml"
  configFiles:
    - configFile:
        type: Git
        spec:
          store:
            type: Github
            spec:
              connectorRef: account.github_org
              repoName: "configs/payment-service"
              paths:
                - "config.prod.yaml"
  variables:
    - name: "replicas"
      type: String
      value: "10"          # Override service default

# In pipeline YAML, service variables:
#   <+serviceVariables.replicas> → "10" (after override resolved)
```

### Environment groups and chaining

```text
[Image: Harness UI → Environments → Environment Groups → + New Group]

Environment groups group multiple environments for batch operations:
  - group "Prod Environments" → environments: [us-east-1-prod, us-west-2-prod]
  - Deploy to all prod environments in one pipeline stage (matrix).
  - Used for: multi-region deployment, sequential staging across envs.
```

---

## Infrastructure Definitions

> [!info] Infrastructure definition
> An infrastructure definition specifies WHERE to deploy (K8s cluster + namespace, ECS cluster + service, SSH host + path). It's associated with an environment and uses a connector (K8s cluster, ECS, SSH).

```yaml
# K8s infrastructure:
infrastructureDefinition:
  name: "prod-us-east-1"
  identifier: prod_us_east_1
  environmentRef: production
  deploymentType: Kubernetes
  spec:
    connectorRef: account.prod_eks_cluster
    namespace: "payment-prod"
    releaseName: "payment-<+service.name>"   # Helm release name
    allowSimultaneousDeployments: false       # Prevent concurrent deploys to same infra

# ECS infrastructure:
infrastructureDefinition:
  name: "ecs-prod"
  identifier: ecs_prod
  environmentRef: production
  deploymentType: ECS
  spec:
    connectorRef: account.aws_prod
    region: "us-east-1"
    cluster: "payment-prod"
    vpcId: "vpc-abc123"
    subnetIds: ["subnet-xxx", "subnet-yyy"]
    securityGroupIds: ["sg-zzz"]
    executionRole: "arn:aws:iam::123456789012:role/ecsExecutionRole"

# SSH infrastructure:
infrastructureDefinition:
  name: "vm-prod"
  identifier: vm_prod
  environmentRef: production
  deploymentType: Ssh
  spec:
    connectorRef: account.vm_prod_connector
    hostArray: "web-servers"
    deploymentType: WINRM           # Or SSH
    loadBalancer: true
    lbDetails:
      loadBalancerType: Classic
      loadBalancerName: "web-lb"
```

### Infrastructure selectors in pipelines

```yaml
# In a CD pipeline stage:
- stage:
    type: Deployment
    spec:
      service: payment_service       # Service defined above
      environment: production
      infrastructure:
        type: KubernetesDirect
        spec:
          connectorRef: account.prod_eks_cluster
          namespace: payment-prod
          releaseName: "payment-<+pipeline.sequenceId>"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for using services/infra in pipelines
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for K8s-specific service config
- [[CICD/Harness/02_Core/02_CD_ECS_Serverless_SSH_Deployments]] for ECS/SSH service config
- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for connector references in services
