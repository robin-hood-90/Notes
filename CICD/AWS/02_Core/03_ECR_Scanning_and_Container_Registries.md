---
tags: [aws, core, ecr, docker, container-registry, image-scanning, lifecycle-policy, pull-through-cache]
aliases: ["ECR Deep Dive", "ECR Scanning", "ECR Lifecycle Policies", "Container Registry"]
status: stable
updated: 2026-05-11
---

# ECR, ECR Scanning, and Container Registries

> [!summary] Goal
> Master Amazon ECR: repositories (private/public), image tags (immutable vs mutable), image scanning (basic with Inspector), lifecycle policies, cross-account access, pull-through cache rules, and authentication for CI/CD.

## Table of Contents

1. [Repositories and Images](#repositories-and-images)
2. [Image Scanning](#image-scanning)
3. [Lifecycle Policies](#lifecycle-policies)
4. [Authentication and CI/CD](#authentication-and-ci-cd)

---

## Repositories and Images

> [!info] ECR
> Amazon ECR is a fully managed container registry that stores Docker images and OCI artifacts. Integrated with ECS, EKS, and Lambda (container images). Private by default. Supports cross-region and cross-account replication.

```bash
# AWS CLI commands:
aws ecr create-repository --repository-name my-app --image-tag-mutability IMMUTABLE
aws ecr describe-repositories
aws ecr list-images --repository-name my-app

# Login:
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and push:
docker build -t my-app .
docker tag my-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:v1
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:v1
```

### Image tags — immutable vs mutable

```text
Mutable (default): tag can be moved to a new image.
  - Risk: v1 can point to different images over time → difficult to roll back.
  - `docker push` with existing tag → tag OVERWRITES.

Immutable: tag can ONLY point to one image (once pushed, cannot be overwritten).
  - Prevents accidental overwrite of production images.
  - Requires new tag per push (e.g., ${{ github.sha }} in CI).
  - Enforce immutable tagging per repository.
```

---

## Image Scanning

| Scan type | Coverage | Frequency | Cost |
|:----------|:---------|:---------:|:----:|
| **Basic** | Package vulnerabilities (OS packages, language libraries) | On push or manual | Free |
| **Enhanced** (Inspector) | OS + programming language + code vulnerabilities | On push + continuous re-scan | Per GB scanned |

```text
Enhanced scanning with Inspector:
  - Detects vulnerabilities in: OS packages (Alpine, Debian, Amazon Linux), programming language packages (Python, Java, Node.js).
  - Continuous scanning: new vulnerabilities are detected even on existing images.
  - Results in: ECR console, Security Hub findings.
  - Suppression: at the vulnerability level (false positives).
  - Filtering: by CVSS score, by package type, by status (FIX_AVAILABLE, NO_FIX).

Basic scanning:
  - On push only (triggered per image push).
  - Uses Clair (open-source scanner).
  - No continuous monitoring.
```

---

## Lifecycle Policies

> [!info] Lifecycle policy
> Lifecycle policies automatically clean up old images based on age or count. Essential for managing storage costs and keeping the repository clean. They only affect images that match the rule (optional tag prefix filtering).

```json
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Expire untagged images older than 14 days",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": 14
            },
            "action": { "type": "expire" }
        },
        {
            "rulePriority": 2,
            "description": "Keep only 3 tagged images per prefix",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["v", "release-"],
                "countType": "imageCountMoreThan",
                "countNumber": 3
            },
            "action": { "type": "expire" }
        }
    ]
}
```

---

## Authentication and CI/CD

### CI/CD authentication (OIDC)

```yaml
# GitHub Actions OIDC → ECR authentication:
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecr
    aws-region: us-east-1

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build, tag, and push
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    IMAGE_TAG: ${{ github.sha }}
  run: |
    docker build -t $ECR_REGISTRY/my-app:$IMAGE_TAG .
    docker push $ECR_REGISTRY/my-app:$IMAGE_TAG
```

### EKS pull-through authentication

```text
EKS nodes need to pull images from ECR. For Fargate, the ECR pull occurs via an execution role.
For EC2 node groups:
  1. ECR credential helper is included in Amazon Linux EKS-optimized AMI.
  2. kubelet uses ecr-credential-provider to get temporary auth tokens.
  3. No manual configuration needed for ECR in the same account.
```

---

## Cross-Links

- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECR → ECS deployments
- [[CICD/AWS/02_Core/02_EKS_Clusters_Node_Groups_and_Pods]] for ECR → EKS pull authentication
- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for ECR cross-account IAM policies
- [[CICD/AWS/05_Projects/01_CI_CD_Pipeline_with_ECS_BlueGreen]] for full CI/CD with ECR
