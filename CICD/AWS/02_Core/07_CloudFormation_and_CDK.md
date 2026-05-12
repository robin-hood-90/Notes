---
tags: [aws, core, cloudformation, cdk, infrastructure-as-code, stacks, change-sets, stack-sets, sam]
aliases: ["CloudFormation Deep Dive", "AWS CDK", "IaC", "Stack Sets", "Change Sets", "SAM"]
status: stable
updated: 2026-05-11
---

# CloudFormation and CDK

> [!summary] Goal
> Master AWS infrastructure as code: CloudFormation (resources, parameters, mappings, conditions, intrinsic functions, change sets, nested stacks, stack sets, drift detection) and CDK (constructs, synth/deploy, multi-environment pipelines, cross-stack references).

## Table of Contents

1. [CloudFormation Template Anatomy](#cloudformation-template-anatomy)
2. [Intrinsic Functions](#intrinsic-functions)
3. [Stack Management](#stack-management)
4. [CDK — Constructs and Pipelines](#cdk-constructs-and-pipelines)

---

## CloudFormation Template Anatomy

> [!info] CloudFormation
> CloudFormation treats infrastructure as code. A template (JSON/YAML) describes AWS resources and their dependencies. CloudFormation provisions and updates them in the correct order.

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "A sample template"
Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0abcdef1234567890
    us-west-2:
      AMI: ami-0b1234567890abcde
Conditions:
  IsProduction: !Equals [!Ref Environment, production]
Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Condition: IsProduction
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
      InstanceType: t3.micro
Outputs:
  InstanceId:
    Description: "The Instance ID"
    Value: !Ref EC2Instance
```

---

## Intrinsic Functions

```yaml
# Ref — reference a resource's physical ID
!Ref MyResource
Ref: MyResource

# Fn::GetAtt — get an attribute from a resource
!GetAtt MyResource.Arn
Fn::GetAtt: [MyResource, Arn]

# Fn::Sub — string interpolation (with variables)
!Sub "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:instance/${Instance}"
Fn::Sub:
  - "arn:aws:${Service}:::${Bucket}"
  - { Service: s3, Bucket: MyBucket }

# Fn::Join — join strings
!Join [":", [a, b, c]]   → "a:b:c"

# Fn::Select — pick from a list
!Select [0, ["a", "b", "c"]]   → "a"

# Fn::FindInMap — look up a mapping
!FindInMap [RegionMap, !Ref "AWS::Region", AMI]

# Fn::ImportValue — import a cross-stack output
!ImportValue SharedVPC-VpcId

# Fn::Base64 — encode for user data
!Base64 !Sub "#!/bin/bash\necho hello"

# Condition functions:
!Equals [a, b]
!And [cond1, cond2]
!Or [cond1, cond2]
!Not [cond]
!If [condition, value_if_true, value_if_false]
```

---

## Stack Management

### Change sets

```text
Change sets preview changes before applying them:
  1. Create ChangeSet: CloudFormation computes diff.
  2. Review changes (additions, modifications, deletions, replacement).
  3. Execute ChangeSet to apply.

Replacement: resource is deleted and recreated (e.g., RDS instance type change).
  - Some changes require replacement (e.g., DB engine version).
  - Other changes are in-place updates (e.g., security group rules).
```

### Nested stacks and StackSets

```text
Nested stacks: embed one stack within another (via AWS::CloudFormation::Stack).
  - Limit: up to 500 total resources per top-level stack.
  - Template URL: must point to S3 (template can be in a bucket).
  - Outputs from nested stacks can be imported via Fn::GetAtt.

StackSets: deploy to multiple accounts/regions from a single template.
  - Self-managed (IAM roles) or service-managed (Organizations).
  - Auto-deploy: automatically deploy to new accounts in an OU.
  - Region concurrency: sequential or parallel.
  - Failure tolerance: percentage of accounts that can fail.
```

### Drift detection

```text
Drift detection: checks if the actual AWS resources match the CloudFormation template.
  - Detects manual changes outside CloudFormation.
  - Reports: drifted/modified/deleted resources.
  - Can add: override policies (retain specific resources on stack deletion).
```

---

## CDK — Constructs and Pipelines

> [!info] CDK
> AWS CDK defines cloud resources using familiar programming languages (TypeScript, Python, Java, C#, Go). It generates CloudFormation templates. Constructs come in three levels: L1 (CFN resources), L2 (high-level defaults), L3 (patterns like `LambdaRestApi`).

```typescript
// CDK example (TypeScript):
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import { App, Stack } from 'aws-cdk-lib';

class MyStack extends Stack {
  constructor(scope: App, id: string) {
    super(scope, id);

    const vpc = new ec2.Vpc(this, 'MyVpc', { maxAzs: 2 });
    const cluster = new ecs.Cluster(this, 'MyCluster', { vpc });
    const service = new ecs.FargateService(this, 'MyService', { cluster });
  }
}
```

### CDK pipeline

```typescript
// Multi-environment CI/CD pipeline with CDK Pipelines:
import { CodePipeline, CodePipelineSource, ShellStep } from 'aws-cdk-lib/pipelines';

class MyPipeline extends Stack {
  constructor(scope: App, id: string) {
    super(scope, id);

    const pipeline = new CodePipeline(this, 'Pipeline', {
      crossAccountKeys: true,
      synth: new ShellStep('Synth', {
        input: CodePipelineSource.gitHub('my-org/my-repo', 'main'),
        commands: [
          'npm ci',
          'npm run build',
          'npx cdk synth',
        ],
      }),
    });

    pipeline.addStage(new MyApplication(this, 'prod', {
      env: { account: '222222222222', region: 'us-east-1' },
    }));
  }
}
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for CloudFormation service role
- [[CICD/AWS/05_Projects/01_CI_CD_Pipeline_with_ECS_BlueGreen]] for pipeline deployments
- [[CICD/AWS/05_Projects/03_Multi_Region_Active_Passive]] for StackSet multi-region deployments
- [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] for Config rules on CloudFormation
