---
tags: [harness, core, sto, security, scanning, sonarqube, trivy, snyk, sbom, grype, bandit, sast, sca, dast, iac-scan, exemption]
aliases: ["Harness STO", "Security Testing Orchestration", "STO Scan", "STO Pipeline", "SBOM Generation", "Security Exemption"]
status: stable
updated: 2026-05-11
---

# Security Testing Orchestration (STO)

> [!summary] Goal
> Master Harness STO: security scan stage types (SAST, SCA, DAST, container scanning, IaC scanning), scan steps (SonarQube, Trivy, Snyk, Grype, Bandit, Aqua, Prisma Cloud, ZAP, Wiz), SBOM generation (CycloneDX/SPDX), exemption management, and integrating security gates into CD pipelines (deny deploy on critical vulnerabilities).

## Table of Contents

1. [STO Scan Types and Steps](#sto-scan-types-and-steps)
2. [SBOM Generation and Exemption Management](#sbom-generation-and-exemption-management)
3. [STO in CD Pipelines](#sto-in-cd-pipelines)

---

## STO Scan Types and Steps

> [!info] STO
> STO ingests results from security scanners (run in CI or directly). Scan types: SAST (static code analysis), SCA (software composition analysis — dependencies), DAST (running app security test), container scanning, IaC scanning (Terraform, CloudFormation). STO normalizes findings into a single view.

### Scan steps

| Step (ingestion mode) | Scanner type | Category |
|:----------------------|:-------------|:---------|
| **Bandit** | Python SAST | SAST |
| **SonarQube** | Multi-language SAST | SAST |
| **Checkmarx** | Multi-language SAST | SAST |
| **Snyk** | Code + dependencies | SAST + SCA |
| **Grype** | Container + dependencies | Container + SCA |
| **Trivy** | Container + IaC + dependencies | Container + SCA + IaC |
| **Aqua Trivy** | Container scanning | Container |
| **Prisma Cloud** | IaC scanning (Terraform, CFN, K8s) | IaC |
| **ZAP** | DAST web application scanning | DAST |
| **Wiz** | Cloud + K8s scanning | IaC + Container |

```yaml
# STO pipeline stage with SonarQube scan:
- stage:
    name: "Security Scan"
    type: Custom
    spec:
      execution:
        steps:
          - step:
              type: Security
              name: "SonarQube Scan"
              spec:
                mode: ingestion               # Run scanner + ingest results
                config:
                  connectorRef: account.sonarqube
                  target:
                    name: "payment-service"
                    type: repository
                    variant: main
                  advanced:
                    args:
                      - "-Dsonar.exclusions=**/test/**"

          - step:
              type: Security
              name: "Trivy Container Scan"
              spec:
                mode: orchestration
                config:
                  connectorRef: account.docker_hub
                  target:
                    name: "<+artifacts.primary.image>"
                    type: container
                  advanced:
                    args:
                      - "--severity=CRITICAL,HIGH"

          - step:
              type: Security
              name: "Snyk IaC Scan"
              spec:
                mode: extraction
                config:
                  connectorRef: account.snyk
                  target:
                    name: "terraform/prod"
                    type: configuration
```

### Scan modes

| Mode | Description |
|:-----|:------------|
| **ingestion** | You run a scanner externally (e.g., in CI step). STO ingests the results (JSON, SARIF, JUnit XML). |
| **orchestration** | STO runs the scanner on your behalf (if the scanner supports it). |
| **extraction** | STO pulls results from a third-party API (e.g., Snyk dashboard, SonarQube API). |

---

## SBOM Generation and Exemption Management

### SBOM (Software Bill of Materials)

```yaml
# Generate SBOM with Syft/Grype:
- step:
    type: Security
    name: "Generate SBOM"
    spec:
      mode: ingestion
      config:
        scanner:
          type: Syft
          spec:
            format: "cyclonedx-json"
        target:
          name: "<+artifacts.primary.image>"
          type: container
        advanced:
          args:
            - "--scope=all-layers"

# Upload to STO for analysis:
- step:
    type: Security
    name: "Analyze SBOM"
    spec:
      mode: ingestion
      config:
        scanner:
          type: Grype
          spec:
            severity: "CRITICAL,HIGH"
```

### Exemption management

```yaml
# Exempt specific CVEs (with expiration):
exemption:
  name: "CVE-2023-12345 Exemption"
  identifier: cve_exemption_1
  target:
    type: container
    name: "payment-service"
  criteria:
    cve: "CVE-2023-12345"
    severity: "medium"
    packageName: "openssl"
    packageVersion: "1.1.1"
  exemptedBy: "platform-team"
  expiryDate: "2026-08-01"
  rationale: "This version of OpenSSL is used for internal-only communication, no external exposure."
```

---

## STO in CD Pipelines

```yaml
# Security gate in CD pipeline: fail deploy if critical vulnerability found:
- stage:
    name: "Deploy to Staging"
    failureStrategies:
      - onFailure:
          errors:
            - STOEvaluationFailed
          action:
            type: RollbackStageOnFailure
    spec:
      execution:
        steps:
          - step:
              type: K8sRollingDeploy
          - step:
              type: Security
              name: "Post-Deploy Scan"
              spec:
                mode: ingestion
                config:
                  scanner:
                    type: Bandit
                  target:
                    name: "<+service.name>"
                    type: repository
                    variant: <+pipeline.variables.artifact_tag>
                settings:
                  failOnSeverity: "CRITICAL"   # Fail pipeline on CRITICAL findings

# STO summary in dashboard:
# [Image: Harness UI → STO → Dashboard]
# Shows: total issues by severity, status (new/ fixed/ exempted/ open), target type, scanner.
```

---

## Cross-Links

- [[CICD/Harness/02_Core/04_CI_Builds_Tests_Caching_and_Test_Intelligence]] for CI + STO integration
- [[CICD/Harness/05_Projects/03_Multi_Stage_CI_CD_with_Security_and_SLO]] for full CI/CD with STO
- [[CICD/Harness/02_Core/01_CD_K8s_Deployments_Rolling_Canary_BlueGreen]] for security-gated CD
- [[CICD/Harness/03_Advanced/02_SRM_SLOs_Error_Tracking_and_Change_Intelligence]] for SLO-based security scores
