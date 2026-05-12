---
tags: [harness, core, ci, build, test, cache, test-intelligence, dinD, kaniko, docker, harness-cloud]
aliases: ["Harness CI", "CI Build Pipeline", "Test Intelligence", "Harness Cloud", "Cache Intelligence", "Docker Build and Push"]
status: stable
updated: 2026-05-11
---

# CI — Builds, Tests, Caching, and Test Intelligence

> [!summary] Goal
> Master Harness CI: CI stages (Build, Run, Plugin, Git Clone), build infrastructure (Harness Cloud, K8s build pods, local runner), Docker build with Kaniko, layer caching, Test Intelligence (selective test execution for impacted code), and cache intelligence for faster builds.

## Table of Contents

1. [CI Pipeline Structure](#ci-pipeline-structure)
2. [Build Infrastructure](#build-infrastructure)
3. [Docker Build and Caching](#docker-build-and-caching)
4. [Test Intelligence](#test-intelligence)

---

## CI Pipeline Structure

> [!info] CI stages
> CI pipelines build, test, and publish artifacts. Harness CI runs steps in containers on build infrastructure (Harness Cloud, K8s cluster, or local runner). Key steps: **Run** (shell script), **Plugin** (marketplace — SonarQube, Snyk, AWS CLI, Slack notify), **BuildAndPushDockerRegistry** (Kaniko or Docker-in-Docker), **Git Clone** (codebase), **Cache** (S3/GCS caching).

```yaml
# CI pipeline example:
pipeline:
  name: "Java CI Pipeline"
  stages:
    - stage:
        name: "Build and Test"
        type: CI
        identifier: build_and_test
        spec:
          cloneCodebase: true
          platform:
            os: Linux
            arch: Amd64
          runtime:
            type: Cloud              # Harness Cloud (fast Linux builder)
          execution:
            steps:
              - step:
                  type: CacheRestore
                  name: "Restore Maven Cache"
                  spec:
                    key: maven-cache-<+pipeline.sequenceId>
                    paths:
                      - /root/.m2/repository
              - step:
                  type: Run
                  name: "Maven Build and Test"
                  spec:
                    shell: Sh
                    command: |
                      mvn clean install -DskipITs
              - step:
                  type: CacheSave
                  name: "Save Maven Cache"
                  spec:
                    key: maven-cache-<+pipeline.sequenceId>
                    paths:
                      - /root/.m2/repository
              - step:
                  type: BuildAndPushDockerRegistry
                  name: "Docker Build & Push"
                  spec:
                    connectorRef: account.aws_ecr
                    tags:
                      - "latest"
                      - <+pipeline.sequenceId>
```

### CI steps

| Step type | Purpose |
|:----------|:--------|
| **Run** | Shell script execution (bash, sh, PowerShell) |
| **Plugin** | Harness marketplace plugins (SonarQube, Snyk, Prisma Cloud, JFrog, AWS CLI, GCP CLI) |
| **BuildAndPushDockerRegistry** | Docker build + push (Kaniko — no DinD needed) |
| **BuildAndPushECR** | Build + push to ECR (uses Kaniko) |
| **BuildAndPushGCR** | Build + push to GCR |
| **Git Clone** | Clone codebase (auto unless disabled) |
| **CacheRestore** | Restore cached directories from S3/GCS |
| **CacheSave** | Save directories to cache |
| **Action** | Run GitHub Actions steps (limited) |
| **SSCA** | Supply chain attestation (SLSA) |

---

## Build Infrastructure

| Infrastructure | Type | Startup | Use case |
|:---------------|:----:|:-------:|:---------|
| **Harness Cloud** | SaaS VM | ~10s | Fastest, no management, Linux/macOS/Windows |
| **K8s Cluster** | Build pods | ~30s | Custom build environments, privileged mode, sidecars |
| **Local Runner** | Your machine | Instant | Dev testing, debugging (Docker Desktop required) |

### Harness Cloud

```yaml
# Use Harness Cloud (fastest — no cluster needed):
runtime:
  type: Cloud
  spec:
    resources:
      memory: "4Gi"
      cpu: 2

# macOS runner:
platform:
  os: macOS
  arch: Arm64

# Windows runner:
platform:
  os: Windows
  arch: Amd64
```

### K8s cluster build infrastructure

```yaml
# K8s build pod (for enterprise with tight security requirements):
runtime:
  type: Kubernetes
  spec:
    connectorRef: account.staging_eks_cluster
    namespace: harness-ci
    podPolicies:
      - type: RunAsNonRoot
      - type: AllowPrivilegeEscalation   # Requires Docker-in-Docker
    resources:
      limits:
        memory: 4Gi
        cpu: 2
    initTimeout: 10m
    # Sidecar for DinD:
    sidecars:
      - image: docker:dind
        name: dind
        entrypoint:
          - dockerd
          - "--tls=false"
          - "--host=tcp://0.0.0.0:2376"
```

---

## Docker Build and Caching

> [!info] Kaniko
> Harness uses Kaniko for Docker builds by default (no Docker socket, no privileged pod required). For ECR/GCR builds, Kaniko is the default builder. Use `BuildAndPushOneConnector` for single-registry push.

```yaml
# Kaniko-based Docker build (default — no DinD needed):
- step:
    type: BuildAndPushDockerRegistry
    name: "Docker Build"
    spec:
      connectorRef: account.docker_hub
      repo: "my-org/app"
      tags:
        - "latest"
        - <+pipeline.sequenceId>
      optimize: true                    # Kaniko optimization
      dockerFile: Dockerfile
      context: .                        # Build context path

# DinD-based build (for complex Dockerfiles needing docker commands):
- step:
    type: BuildAndPushDockerRegistry
    name: "Docker Build with DinD"
    spec:
      connectorRef: account.aws_ecr
      dockerFetcher: DinD               # Use Docker-in-Docker
      tags:
        - "latest"
        - <+pipeline.sequenceId>
```

### Cache intelligence

```yaml
# Cache Intelligence automatically detects cache for:
# Java (Maven ~/.m2), Node (node_modules), Python (~/.cache/pip), Go (~/go/pkg/mod)
# Ruby (vendor/bundle), .NET (~/.nuget/packages)

- step:
    type: CacheRestore
    name: "Restore Cache"
    spec:
      key: cache-<+pipeline.sequenceId>
      paths:
        - /root/.m2/repository
        - /root/.gradle/caches

# Use a fallback key to restore the LAST successful cache (even if sequence ID changed):
key: cache-<+pipeline.sequenceId>
paths:
  - /root/.m2/repository
restoreKeys:
  - cache-                         # Fallback: cache-111, cache-110, etc.
```

---

## Test Intelligence

> [!info] Test Intelligence
> Harness Test Intelligence runs ONLY the tests that are impacted by code changes (selective test execution). For example, if you change file A and test A, only test A runs — NOT test B, C, D, etc. This cuts build time by 40-70%. Supported languages: Java (Maven, Gradle), JavaScript/TypeScript (Jest), Python (pytest), Go (go test), Ruby (RSpec), .NET (xUnit, NUnit, MSTest).

```yaml
# Enabling Test Intelligence:
- step:
    type: Run
    name: "Run Tests with TI"
    spec:
      shell: Sh
      command: mvn test               # Standard test command
      enableTestIntelligence: true     # ← This activates TI!
      testReport:
        type: JUnit
        spec:
          paths:
            - "**/target/surefire-reports/*.xml"
            - "**/target/failsafe-reports/*.xml"
      language: Java
      buildTool: Maven

# TI workflow:
# 1. Harness runs the build to compile code (Maven, Gradle, etc.).
# 2. Harness runs the `mvn test` command with TI enabled.
# 3. TI determines which tests are impacted by the git changes (diff from the PR).
# 4. ONLY impacted tests are executed.
# 5. Test results are reported in Harness UI (pass/fail, time, coverage).

# JS/TS example with TI:
- step:
    name: "Jest Tests"
    type: Run
    spec:
      command: npm test
      enableTestIntelligence: true
      language: JavaScript
      buildTool: Jest
      testReport:
        type: JUnit
        spec:
          paths:
            - "junit.xml"
```

### Test reports and coverage

```yaml
# Collect test results from CI:
- step:
    type: Run
    name: "Report Tests"
    spec:
      command: npm run test:ci
      reports:
        type: JUnit
        spec:
          paths:
            - "junit.xml"

# Code coverage:
- step:
    type: Run
    name: "Generate Coverage"
    spec:
      command: npm run coverage
      reports:
        type: JaCoCo
        spec:
          paths:
            - "**/jacoco.exec"
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/08_Templates_and_Git_Experience]] for CI pipeline templates
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for CD pipelines after CI
- [[CICD/Harness/02_Core/08_STO_Security_Testing_Orchestration]] for adding security scans to CI
- [[CICD/Harness/05_Projects/03_Multi_Stage_CI_CD_with_Security_and_SLO]] for full CI/CD project
