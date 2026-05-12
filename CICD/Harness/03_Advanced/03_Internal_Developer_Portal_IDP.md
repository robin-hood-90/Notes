---
tags: [harness, advanced, idp, developer-portal, software-catalog, scorecard, self-service, backstage, plugins]
aliases: ["Harness IDP", "Internal Developer Portal", "Software Catalog", "Scorecards", "Self-Service Actions", "Software Templates"]
status: stable
updated: 2026-05-11
---

# Internal Developer Portal (IDP) — Software Catalog and Scorecards

> [!summary] Goal
> Master Harness IDP (Backstage-based): software catalog (entities: components, resources, APIs), scorecards (evaluate entities against rules — check for README, Dockerfile, CI/CD config, security scans, OnCall in PagerDuty), self-service actions (create new service from template, register new app in the catalog), and plugins.

## Table of Contents

1. [Software Catalog and Entity Registration](#software-catalog-and-entity-registration)
2. [Scorecards and Rules](#scorecards-and-rules)
3. [Self-Service Actions and Software Templates](#self-service-actions-and-software-templates)

---

## Software Catalog and Entity Registration

> [!info] Catalog entities
> The software catalog (Backstage-based) tracks all software components: services, libraries, websites, data pipelines, and more. Entities are registered via YAML files stored in Git repos. Each entity has metadata (name, description, team, lifecycle) and spec (type, owner, system, dependsOn).

### Catalog entity YAML

```yaml
# catalog-info.yaml (stored in each service's Git repo):
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: "payment-service"
  description: "Handles payment processing"
  tags:
    - java
    - spring-boot
    - service
  annotations:
    github.com/project-slug: my-org/payment-service
    harness.io/project-url: https://app.harness.io/ng/account/XXX/home/orgs/platform-eng/projects/payment
    sonarqube.org/project-key: payment-service
spec:
  type: service
  lifecycle: production
  owner: team-payment
  system: payment-platform
  dependsOn:
    - component:accounting-database
    - resource:payment-api-spec
  providesApis:
    - payment-api
```

### Catalog entities by type

| Kind | Description | Example |
|:-----|:------------|:--------|
| **Component** | Software component (service, library, website) | `payment-service` |
| **API** | API specification (OpenAPI, GraphQL) | `payment-api` |
| **Resource** | Infrastructure resource (DB, queue) | `payment-postgres` |
| **System** | Group of components/resources | `payment-platform` |
| **Domain** | Business domain | `e-commerce` |
| **Group** | Team/ org | `team-payment` |
| **User** | Individual | `alice@mycompany.com` |

---

## Scorecards and Rules

> [!info] Scorecards
> Scorecards evaluate catalog entities against rules. Rules are checks: "does entity have a README?", "does entity have CI/CD pipeline?", "does entity use HTTPS only?", "does entity have a PagerDuty OnCall?". Scorecards produce a score (0-100%) for each entity.

### Scorecard rules

```yaml
scorecard:
  name: "Production Readiness"
  identifier: production_readiness
  rules:
    - rule:
        name: "Has README"
        identifier: has_readme
        type: RepositoryContainsFile
        spec:
          filePath: "README.md"
    - rule:
        name: "Has CI/CD Pipeline"
        identifier: has_cicd
        type: HarnessPipelineExists
        spec:
          pipelineName: "deploy-<+entity.name>"
    - rule:
        name: "Dockerfile Exists"
        identifier: has_dockerfile
        type: RepositoryContainsFile
        spec:
          filePath: "Dockerfile"
    - rule:
        name: "Security Scan Passed"
        identifier: security_scan
        type: HarnessSecurityScan
        spec:
          scanType: "SAST"
    - rule:
        name: "Has OnCall"
        identifier: has_oncall
        type: PagerDutyService
        spec:
          pagerdutyServiceName: "<+entity.name>"
    - rule:
        name: "Has OpenAPI Spec"
        identifier: has_openapi
        type: RepositoryContainsFile
        spec:
          filePath: "openapi.yaml"
```

---

## Self-Service Actions and Software Templates

> [!info] Self-Service actions
> Self-service actions let developers perform tasks from the Harness IDP without going to DevOps: "Create a new microservice" → fill form → pipeline scaffolds repo + sets up CI/CD + registers in catalog. Self-service actions are powered by Harness pipelines under the hood.

### Software template

```yaml
# Self-service action template:
template:
  name: "Create New Microservice"
  identifier: create_microservice
  spec:
    input:
      - name: "serviceName"
        title: "Service Name"
        type: string
        pattern: "^[a-z-]+$"
      - name: "team"
        title: "Team"
        type: string
        enum: ["payment", "platform", "data"]
      - name: "language"
        title: "Language"
        type: string
        enum: ["Java", "Go", "Node"]
      - name: "repoUrl"
        title: "Repository URL"
        type: string
    steps:
      - run:
          action: "Create Repository"
          spec:
            repoName: <+inputs.serviceName>
            templateRepo: "my-org/service-template"
      - run:
          action: "Create CI/CD Pipeline"
          spec:
            pipelineTemplate: "ci-cd-pipeline-template"
            pipelineName: <+inputs.serviceName>
      - run:
          action: "Register in Catalog"
          spec:
            entityTemplate: "component-template"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for templates underlying IDP
- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI templates used in IDP
- [[CICD/Harness/03_Advanced/03_Internal_Developer_Portal_IDP]] for this module
- [[CICD/Harness/03_Advanced/04_SEI_DORA_Metrics_and_Engineering_Insights]] for DORA scores in the portal
