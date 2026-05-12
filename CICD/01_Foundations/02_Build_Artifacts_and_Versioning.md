---
tags: [cicd, foundations, artifacts, versioning, registries, containers, signing, sbom]
aliases: ["Build Artifacts", "Versioning", "Artifact Registries", "SemVer", "Artifact Signing"]
status: stable
updated: 2026-05-11
---

# Build Artifacts and Versioning

> [!summary] Goal
> Build once, deploy many. Understand artifact types (container image, JAR, tarball, static bundle, SBOM), registries (ECR, Docker Hub, Artifactory, GHCR), versioning strategies (SemVer, CalVer, Git SHA, build number), immutable vs mutable tags, multi-arch images, artifact signing with cosign, and SBOM generation.

## Table of Contents

1. [Artifact Types](#artifact-types)
2. [Versioning Strategies](#versioning-strategies)
3. [Registries and Promotion](#registries-and-promotion)
4. [Artifact Signing and SBOM](#artifact-signing-and-sbom)

---

## Artifact Types

> [!info] Artifact
> An artifact is the output of a CI build that is deployed or consumed by another process. Artifacts must be immutable: once published, they never change. Deployments reference a specific artifact version.

| Artifact type | Example | Registry | How to reference |
|:--------------|:--------|:---------|:-----------------|
| **Container image** | `my-app:git-abc1234` | ECR, Docker Hub, GCR, ACR, Artifactory, Nexus | `docker pull` by digest (`my-app@sha256:...`) or tag |
| **JAR/WAR** | `my-app-1.2.3.jar` | Artifactory, Nexus, S3, Maven Central | Maven/Gradle dependency reference |
| **npm package** | `my-app@1.2.3` | npm registry, GitHub Packages, Verdaccio | `npm install` with exact version |
| **Tarball / zip** | `my-app-v1.2.3.tar.gz` | S3, GCS, Artifactory, GitHub Releases | S3 key or URL |
| **Helm chart** | `my-app-1.2.3.tgz` | OCI registry, Helm repo (S3/GCS/Artifact Hub) | `helm install` with version |
| **Static bundle** | `build/` directory (JS, CSS, HTML) | S3, CloudFront, npm, GitHub Pages | URL with version in path |
| **SBOM** | `my-app-1.2.3.spdx.json` | S3, same registry alongside artifact | Attached as artifact metadata |

---

## Versioning Strategies

> [!info] Versioning
> Every artifact needs a unique, immutable identifier. The strategy depends on the artifact type, team workflow, and whether consumers need SemVer compatibility.

| Strategy | Format | Example | Best for |
|:---------|:-------|:--------|:---------|
| **Git SHA** | `git-<sha>` | `git-abc1234def5678` | Internal services, microservices, decoupled teams |
| **Build number** | `<build-number>` | `1234`, `20260511.1` | Sequential CI systems (Jenkins, GitLab CI) |
| **SemVer** | `<major>.<minor>.<patch>` | `1.2.3`, `2.0.0-rc.1` | Libraries, mobile apps, consumer-facing APIs |
| **CalVer** | `<YYYY>.<MM>.<patch>` | `2026.05.1` | SaaS, rolling releases |
| **Combined** | `<semver>+<build>` | `1.2.3+build.5678` | Traceable, human-readable versions |

### SemVer rules for CI/CD

```text
Given a version MAJOR.MINOR.PATCH:
  MAJOR: incompatible API changes (can't deploy with old consumers).
  MINOR: backward-compatible feature added (safe to deploy).
  PATCH: backward-compatible bug fix (safe to deploy).
  Pre-release: v1.0.0-alpha, v1.0.0-rc.1 (not for production).

Internal services:
  - Use Git SHA (no need for SemVer — no external consumers).
  - The exact commit is the only reliable identifier.

Libraries:
  - SemVer is the standard. Publish to a package registry.
  - Include build metadata: v1.2.3+build.5678 for traceability.

Deploy tag immutability:
  - Mutable tags (latest) are FOR LOCAL DEV only.
  - Production deployments always reference immutable identifier.
  - Stable tags (e.g., stable) are useful for quick rollbacks but are mutable — move them after deploy validation.
```

---

## Registries and Promotion

| Registry | Artifact types | Auth | Geo-replication | Best for |
|:---------|:--------------|:----:|:---------------:|----------|
| **ECR** (AWS) | Container images | IAM, OIDC | Per-region | AWS users |
| **Docker Hub** | Container images | Username/token | Global | Open-source, small teams |
| **GCR/Artifact Registry** | Container images | Service account | Global | GCP users |
| **ACR** (Azure) | Container images | Azure AD | Geo-replication | Azure users |
| **Artifactory** | All types (JAR, npm, Docker, Helm) | Token + LDAP | Enterprise federation | Enterprise, hybrid clouds |
| **Nexus** | All types | Token + LDAP | Single-region | Self-hosted, air-gapped |
| **GitHub Packages** | npm, Docker, Maven, NuGet | GitHub token | Global | GitHub-centric teams |
| **GHCR** (GitHub Container Registry) | Container images | GitHub token | Global | GitHub Actions users |

### Promotion flow

```text
Build CI                         Registry                             Deploy
──────                           ────────                             ──────
Commit → `docker build`          Push `git-abc123`                     Staging: pull `git-abc123`
                                 Push `git-def456`                     Staging: pull `git-def456`
                                 Push `git-ghi789`                     Staging: pull `git-ghi789`
                                                                       Approval gate
                                                                       Prod: pull `git-ghi789`
                                                                       Move `stable` tag → `git-ghi789`
```

---

## Artifact Signing and SBOM

> [!info] Signing
> Signing ensures the artifact hasn't been tampered with between build and deploy. Cosign (Sigstore) is the standard for container signing — it supports keyless signing backed by OIDC identity. Signatures are stored in the registry alongside the artifact.

```bash
# Sign a container image with cosign (keyless — recommended):
cosign sign my-registry/my-app@sha256:abc123

# Verify:
cosign verify my-registry/my-app@sha256:abc123 \
  --certificate-identity email@mycompany.com

# Signature stored as a separate tag: my-app@sha256-abc123.sig
```

### SBOM (Software Bill of Materials)

```text
SBOM is a record of all components in an artifact. It's generated during build
(by Syft, Trivy, or other tools) and stored alongside the artifact.

Standard formats:
  - SPDX (Linux Foundation) — most common.
  - CycloneDX (OWASP) — widely used, richer dependency graph.

Use: vulnerability scanning (Trivy scans SBOM), compliance (attest to
what's in your artifact), supply chain transparency (share with customers).

Generate SBOM in CI:
  syft packages my-app:git-abc1234 -o spdx-json > sbom.spdx.json
  Store sbom.spdx.json in the registry or attached to the release.
```

---

## Cross-Links

- [[CICD/01_Foundations/01_Pipelines_Basics]] for pipeline stages and promotion flow
- [[CICD/Docker/01_Foundations/01_Images_Containers_and_Layers]] for container images
- [[CICD/AWS/02_Core/03_ECR_Scanning_and_Container_Registries]] for ECR lifecycle policies
- [[CICD/GitHub/01_Foundations/03_Releases_Tags_and_Changelogs]] for GitHub Releases
