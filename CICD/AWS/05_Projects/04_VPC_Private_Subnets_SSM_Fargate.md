---
tags: [aws, project, vpc, networking, fargate, ssm, ecs, private-subnet, nat-gateway, vpc-endpoint]
aliases: ["VPC Private Subnets SSM Fargate", "ECS Fargate Private VPC", "SSM VPC Endpoints"]
status: stable
updated: 2026-05-11
---

# Project: VPC with Private Subnets, SSM, and ECS Fargate

> [!summary] Goal
> Build a VPC with public/private subnets, deploy ECS Fargate tasks into private subnets, connect via SSM Session Manager (no public IP, no bastion), and configure VPC Endpoints for ECR, CloudWatch Logs, S3, and SSM.

## Architecture

```text
VPC (10.0.0.0/16):
  Public subnet (10.0.1.0/24): ALB, NAT Gateway
  Private subnet (10.0.2.0/24): ECS Fargate tasks

VPC Endpoints:
  - SSM (com.amazonaws.us-east-1.ssmmessages)
  - ECR API + DKR (com.amazonaws.us-east-1.ecr.api, ecr.dkr)
  - S3 (Gateway Endpoint — free)
  - CloudWatch Logs (com.amazonaws.us-east-1.logs)

SSM Session Manager: connect to Fargate tasks without public IP.
```

### CloudFormation (VPC)

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  NATGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt EIP.AllocationId
      SubnetId: !Ref PublicSubnet

  SSMEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: com.amazonaws.us-east-1.ssmmessages
      VpcId: !Ref VPC
      SubnetIds: [!Ref PrivateSubnet]
      PrivateDnsEnabled: true
```

### ECS Cluster + Service (Private Subnet)

```yaml
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: my-cluster

  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      RequiresCompatibilities: [FARGATE]
      NetworkMode: awsvpc
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: nginx:latest
          Essential: true
          PortMappings:
            - ContainerPort: 80

  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: [!Ref PrivateSubnet]
          SecurityGroups: [!Ref TaskSecurityGroup]
          AssignPublicIp: DISABLED
      LoadBalancers:
        - ContainerName: app
          ContainerPort: 80
          TargetGroupArn: !Ref TargetGroup
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC networking
- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS Fargate
- [[CICD/AWS/03_Advanced/03_SSM_Session_Manager_and_SSH]] for SSM Session Manager
- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC Endpoints
