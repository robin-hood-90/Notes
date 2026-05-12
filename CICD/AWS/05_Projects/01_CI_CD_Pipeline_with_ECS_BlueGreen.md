---
tags: [aws, project, cicd, ecs, ecr, blue-green, codedeploy, github-actions, oidc]
aliases: ["CI/CD ECS Pipeline", "Blue/Green Deployment on ECS", "GitHub Actions ECS Deploy"]
status: stable
updated: 2026-05-11
---

# Project: CI/CD Pipeline with ECS and Blue/Green

> [!summary] Goal
> Build a complete CI/CD pipeline: GitHub Actions OIDC → AWS IAM role → ECR image build → ECS deploy via CodeDeploy (Blue/Green with traffic shifting, test listener, auto-rollback).

## Architecture

```text
GitHub Actions → OIDC assume IAM role → Build image → Push to ECR → CodeDeploy
→ Deploy to ECS (Green) → Route 10% traffic via test listener → Validate → Shift 100%
→ If CloudWatch alarm → Auto-rollback
```

### IAM Role for GitHub Actions

```json
{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike": { "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main" }
    }
}
```

### CodeDeploy AppSpec (appspec.yaml)

```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: "arn:aws:ecs:us-east-1:ACCOUNT:task-definition/my-app:1"
        LoadBalancerInfo:
          ContainerName: "app"
          ContainerPort: 80
```

---

## Cross-Links

- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS service definition
- [[CICD/AWS/02_Core/03_ECR_Scanning_and_Container_Registries]] for ECR image push
- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for OIDC IAM role
- [[CICD/GitHubActions/02_Core/01_Secrets_Environments_and_OIDC]] for GitHub Actions OIDC
