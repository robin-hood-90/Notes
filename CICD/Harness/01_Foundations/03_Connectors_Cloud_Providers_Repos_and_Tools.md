---
tags: [harness, foundations, connectors, kubernetes, aws, git, docker, helm, jira, servicenow, pagerduty]
aliases: ["Harness Connectors", "Kubernetes Connector", "AWS Connector", "Git Connector", "Docker Connector", "Helm Connector"]
status: stable
updated: 2026-05-11
---

# Connectors — Cloud Providers, Repos, and External Tools

> [!summary] Goal
> Master Harness connectors for integrating with external systems: Kubernetes clusters, AWS/GCP/Azure, Git providers (GitHub/GitLab/Bitbucket), Docker/ECR/GCR registries, Helm repos, and notification tools (Jira, ServiceNow, PagerDuty, Slack). Understand credential types, delegate requirements, and test connection process.

## Table of Contents

1. [Connector Types and Setup](#connector-types-and-setup)
2. [Kubernetes Connector](#kubernetes-connector)
3. [AWS and Cloud Connectors](#aws-and-cloud-connectors)
4. [Git and Registry Connectors](#git-and-registry-connectors)

---

## Connector Types and Setup

> [!info] Connector
> A connector stores credentials to connect to an external system. Connectors are used by pipelines to: deploy to clusters, pull artifacts, clone repos, send notifications, run terraform, etc. Connectors are configured at Project, Org, or Account scope. Each connector must pass a "test connection" before it can be used.

### Connector categories

| Category | Connector types |
|:---------|:----------------|
| **Cloud Providers** | Kubernetes, AWS, GCP, Azure, Tanzu, OpenShift, PCF |
| **Source Repos** | GitHub, GitLab, Bitbucket, Azure Repo, CodeCommit, Harness Code |
| **Docker Registries** | Docker Hub, ECR, GCR, ACR, Harbor, Artifactory, Nexus, Quay |
| **Artifacts** | S3, GCS, JFrog Artifactory, Nexus, Sonatype, Jenkins |
| **Helm Repos** | HTTP Helm, OCI Helm (ECR/GCR), Harness Helm |
| **Monitoring** | Prometheus, Datadog, New Relic, AppDynamics, Splunk, Grafana, ELK |
| **Notifications** | Slack, PagerDuty, Jira, ServiceNow, Microsoft Teams |
| **Others** | Terraform (GCS, S3 backend), Vault, HashiCorp Cloud |

### Setup workflow

```text
[Image: Harness UI → Setup → Connectors → + Add New Connector]

Steps:
  1. Navigate to Project Setup → Connectors.
  2. Click "+ New Connector".
  3. Select connector type (e.g., "Kubernetes Cluster").
  4. Name and description (e.g., "prod-eks-cluster").
  5. Specify details (URL, credentials, region, etc.).
  6. Select connectivity mode: "Connect via Harness Delegate".
  7. Choose delegate selectors (e.g., "env:prod").
  8. Test connection (verifies the connector works).
  9. Save and use in pipelines.
```

---

## Kubernetes Connector

> [!info] K8s connector
> Connect to any Kubernetes cluster (EKS, AKS, GKE, self-managed, OpenShift). The connector stores the cluster master endpoint URL and either a service account token or delegate credentials.

```yaml
# Kubernetes connector YAML (with delegate inheritance):
connector:
  name: "prod-eks-cluster"
  identifier: prod_eks_cluster
  type: K8sCluster
  spec:
    credential:
      type: InheritFromDelegate
    delegateSelectors:
      - env:prod
      - team:platform

# K8s connector with explicit service account token:
connector:
  name: "staging-k8s"
  identifier: staging_k8s
  type: K8sCluster
  spec:
    credential:
      type: ManualConfig
      spec:
        masterUrl: "https://XXX.gr7.us-east-1.eks.amazonaws.com"
        auth:
          type: ServiceAccount
          spec:
            serviceAccountTokenRef: account.sa_token  # Secret reference
    delegateSelectors:
      - team:platform
```

### Service account permissions for delegate

```yaml
# The delegate's K8s service account needs these permissions for deployments:
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: harness-delegate-role
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets", "daemonsets"]
    verbs: ["*"]
  - apiGroups: ["batch"]
    resources: ["jobs", "cronjobs"]
    verbs: ["*"]
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets", "namespaces", "events"]
    verbs: ["*"]
```

---

## AWS and Cloud Connectors

### AWS connector

```yaml
# AWS connector with IAM keys:
connector:
  name: "aws-prod"
  identifier: aws_prod
  type: Aws
  spec:
    credential:
      type: ManualConfig
      spec:
        accessKey: "AKIAIOSFODNN7EXAMPLE"
        secretKeyRef: account.aws_secret_key   # Secret reference
    region: "us-east-1"
    delegateSelectors:
      - env:prod

# AWS connector with IRSA (IAM Roles for Service Accounts):
# Requires delegate with IRSA annotation:
connector:
  name: "aws-prod-irsa"
  identifier: aws_prod_irsa
  type: Aws
  spec:
    credential:
      type: InheritFromDelegate   # Delegate uses its own IRSA role
    region: "us-east-1"
    delegateSelectors:
      - env:prod
```

### GCP connector

```yaml
connector:
  name: "gcp-prod"
  identifier: gcp_prod
  type: Gcp
  spec:
    credential:
      type: ManualConfig
      spec:
        secretKeyRef: account.gcp_service_account_key  # JSON key
    delegateSelectors:
      - team:platform
```

### GCP OIDC

```yaml
connector:
  name: "gcp-prod-oidc"
  identifier: gcp_prod_oidc
  type: Gcp
  spec:
    credential:
      type: OidcAuthentication
      spec:
        workloadPoolUrl: "https://iam.googleapis.com/projects/XXX/locations/global/workloadIdentityPools/YYY"
        providerId: "harness"
        gcpProjectId: "my-gke-project"
        serviceAccountEmail: "harness-deploy@my-gke-project.iam.gserviceaccount.com"
    delegateSelectors:
      - team:platform
```

---

## Git and Registry Connectors

### Git connectors (GitHub, GitLab, Bitbucket)

```yaml
# GitHub connector with SSH key:
connector:
  name: "github-org"
  identifier: github_org
  type: Github
  spec:
    url: "https://github.com/my-org"
    authentication:
      type: Ssh Key
        spec:
          credentialRef: account.github_ssh_key   # SSH key secret
    apiAccess:
      type: Token
      spec:
        tokenRef: account.github_api_token   # Personal Access Token
    delegateSelectors:
      - team:platform

# GitLab connector with HTTP credentials:
connector:
  name: "gitlab-internal"
  identifier: gitlab_internal
  type: Gitlab
  spec:
    url: "https://gitlab.internal.com"
    authentication:
      type: Http
      spec:
        type: UsernamePassword
        spec:
          username: "harness-bot"
          passwordRef: account.gitlab_password
    apiAccess:
      type: Token
      spec:
        tokenRef: account.gitlab_api_token
    delegateSelectors:
      - team:platform
```

### Docker connector

```yaml
connector:
  name: "docker-hub"
  identifier: docker_hub
  type: DockerRegistry
  spec:
    dockerRegistryUrl: "https://index.docker.io/v2/"
    auth:
      type: UsernamePassword
      spec:
        username: "my-user"
        passwordRef: account.docker_password
    delegateSelectors:
      - team:platform
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/02_Delegates_Installation_Sizing_Operations]] for delegate selectors
- [[CICD/Harness/01_Foundations/04_Secrets_Managers_SSH_Keys_and_Files]] for secret references in connectors
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for using connectors in real pipeline
- [[CICD/Harness/04_Playbooks/02_Troubleshoot_Pipeline_Failures]] for connector test failures
