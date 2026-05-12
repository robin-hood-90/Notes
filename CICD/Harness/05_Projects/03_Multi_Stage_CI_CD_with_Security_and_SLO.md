---
tags: [harness, project, ci, cd, sto, security, slo, srm, multi-stage, chaos, approval]
aliases: ["Multi-Stage CI/CD with Security and SLO", "Full Lifecycle Pipeline"]
status: stable
updated: 2026-05-11
---

# Project: Multi-Stage CI/CD with Security Scan and SLO Validation

> [!summary] Goal
> Build a full lifecycle pipeline: CI build (Java/Spring Boot) → SonarQube scan (STO) → Docker build/push → deploy to staging via K8s rolling → chaos experiment (verify resilience) → load test → human approval → deploy to prod via blue/green → update SLO in SRM.

## Architecture

```text
[CI: Maven Build → Tests → Test Intelligence]
  → [STO: SonarQube SAST + Trivy Container Scan]
    → [Docker Build → Push to ECR]
      → [CD: Deploy to Staging → Helm Rolling]
        → [Chaos: pod-delete → Verify Resilience]
          → [Load Test: Check p99 Latency < 500ms]
            → [Approval: Human decision]
              → [CD: Deploy to Prod → Blue/Green]
                → [SRM: Update SLO Dashboard]
```

### CI Stage

```yaml
- stage:
    name: "Build and Test"
    type: CI
    spec:
      cloneCodebase: true
      runtime:
        type: Cloud
      execution:
        steps:
          - step:
              type: CacheRestore
              name: "Restore Maven"
              spec:
                key: maven-cache
                paths:
                  - /root/.m2/repository
          - step:
              type: Run
              name: "Maven Build"
              spec:
                command: mvn clean install
                enableTestIntelligence: true
                language: Java
                buildTool: Maven
          - step:
              type: CacheSave
              name: "Save Maven"
              spec:
                key: maven-cache
                paths:
                  - /root/.m2/repository
          - step:
              type: Security
              name: "SonarQube"
              spec:
                mode: ingestion
                config:
                  connectorRef: account.sonarqube
          - step:
              type: BuildAndPushDockerRegistry
              name: "Docker Build"
              spec:
                connectorRef: account.aws_ecr
                tags:
                  - "latest"
                  - <+pipeline.sequenceId>
          - step:
              type: Security
              name: "Trivy Scan"
              spec:
                mode: ingestion
                config:
                  scanner:
                    type: Trivy
```

### CD + Chaos + SLO

```yaml
- stage:
    name: "Deploy to Staging"
    type: Deployment
    spec:
      service: payment-service
      environment: staging
      execution:
        steps:
          - step:
              type: K8sRollingDeploy
          - step:
              type: Chaos
              name: "Pod Kill"
              spec:
                experimentRef: payment_pod_delete
          - step:
              type: Http
              name: "Check Health"
              spec:
                url: "http://payment-service.staging/health"
                assertion: "<+httpResponseCode> == 200"
```

---

## Cross-Links

- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI stage
- [[CICD/Harness/02_Core/08_STO_Security_Testing_Orchestration]] for SonarQube/Trivy
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for deploy stages
- [[CICD/Harness/03_Advanced/02_SRM_SLOs_Error_Tracking_and_Change_Intelligence]] for SLO update
