---
tags: [aws, advanced, ssm, session-manager, ssh, ec2-instance-connect, bastion, port-forwarding, patch-manager, automation]
aliases: ["SSM Session Manager", "SSH into EC2", "Bastion Host", "EC2 Instance Connect", "SSM Automation", "Patch Manager"]
status: stable
updated: 2026-05-11
---

# SSM, Session Manager, EC2 Instance Connect, and SSH

> [!summary] Goal
> Master every way to connect to EC2 instances: SSH key pairs (`.pem` files, `ssh-agent`, SSH config), bastion hosts (jump boxes, proxy jumps), EC2 Instance Connect (one-time SSH key push), and Systems Manager Session Manager (agent-based, no SSH, no public IP). Compare approaches for security and auditability.

## Table of Contents

1. [SSH into EC2 — Keys, Agents, Config](#ssh-into-ec2-keys-agents-config)
2. [Bastion Hosts and Proxy Jumps](#bastion-hosts-and-proxy-jumps)
3. [EC2 Instance Connect](#ec2-instance-connect)
4. [Systems Manager Session Manager](#systems-manager-session-manager)
5. [SSH over Session Manager](#ssh-over-session-manager)
6. [Comparison and Decision Guide](#comparison-and-decision-guide)

---

## SSH into EC2 — Keys, Agents, Config

> [!info] SSH key pairs
> EC2 key pairs consist of a public key (stored by AWS) and a private key (downloaded as `.pem` at launch). The public key is placed in `~/.ssh/authorized_keys` on the instance. Only the private key holder can SSH in.

```bash
# Permission fix (required for .pem files):
chmod 400 my-key.pem

# Basic SSH:
ssh -i my-key.pem ec2-user@54.123.45.67

# Using ssh-agent (no need to specify -i each time):
ssh-add my-key.pem
ssh ec2-user@54.123.45.67

# SSH config (~/.ssh/config) — per-host configuration:
Host my-instance
    HostName 54.123.45.67
    User ec2-user
    IdentityFile ~/.ssh/my-key.pem
    Port 22
# Then: ssh my-instance
```

```text
EC2 usernames by AMI:
  - Amazon Linux 2/2023: ec2-user
  - Ubuntu: ubuntu
  - RHEL: ec2-user
  - Debian: admin
  - CentOS: centos
  - Fedora: ec2-user
```

---

## Bastion Hosts and Proxy Jumps

> [!info] Bastion host
> A bastion (jump box) is a hardened EC2 instance in a public subnet that provides SSH access to instances in private subnets. The user SSH into the bastion first, then SSH from the bastion to the private instances (SSH forwarding).

```bash
# SSH with proxy jump (one command, no manual intermediate SSH):
ssh -J ec2-user@bastion-ip ec2-user@10.0.1.50
# Uses SSH forwarding: client → bastion → target (private IP)

# SSH Agent forwarding:
ssh -A ec2-user@bastion-ip
# On the bastion, you can then SSH with your local key: ssh ec2-user@10.0.1.50

# Auto scaling bastion:
#   - Use an ASG with min=1, max=3 (one per AZ).
#   - Security group: port 22 from corp CIDR.
#   - Bastion AMI: hardened (minimal packages, no passwords).
#   - Session logging: bastion logs SSH sessions to CloudWatch.
```

---

## EC2 Instance Connect

> [!info] EC2 Instance Connect
> EC2 Instance Connect (EIC) pushes a one-time SSH public key to the instance for 60 seconds. The key is tied to an IAM principal, providing full audit trail via CloudTrail. No permanent SSH key file to manage.

```bash
# Prerequisites:
# 1. Instance must have `ec2-instance-connect` package.
# 2. IAM policy must allow `ec2-instance-connect:SendSSHPublicKey`.
# 3. Instance metadata must be reachable from the SSH protocol.

# One-time key push:
aws ec2-instance-connect send-ssh-public-key \
    --instance-id i-1234567890abcdef0 \
    --availability-zone us-east-1a \
    --instance-os-user ec2-user \
    --ssh-public-key file://~/.ssh/id_rsa.pub

# Then SSH normally (within 60 seconds):
ssh ec2-user@54.123.45.67

# Browser-based SSH in AWS Console:
# No AWS CLI needed — click "Connect" → "EC2 Instance Connect" in the console.
```

---

## Systems Manager Session Manager

> [!info] Session Manager
> SSM Session Manager provides secure, auditable shell access to EC2 and on-prem instances WITHOUT opening SSH ports, WITHOUT a bastion host, and WITHOUT public IPs. It uses the SSM Agent installed on the instance.

### Requirements

```text
1. SSM Agent installed (Amazon Linux 2/2023, Ubuntu, Windows — included or installable).
2. IAM role with `AmazonSSMManagedInstanceCore` policy.
3. Instance can reach SSM endpoints (via VPC endpoints for private subnets).
4. Session Manager plugin installed on the client machine.

VPC Endpoints required for Session Manager in private subnets:
  - com.amazonaws.region.ssmmessages — session data channel.
  - com.amazonaws.region.ssm — control channel.
  - com.amazonaws.region.ec2messages — EC2 status.
```

### IAM permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession",
                "ssm:TerminateSession",
                "ssm:ResumeSession"
            ],
            "Resource": "*"
        }
    ]
}
```

### Usage

```bash
# Start a session:
aws ssm start-session --target i-1234567890abcdef0

# Port forwarding (access private DB without SSH):
aws ssm start-session \
    --target i-1234567890abcdef0 \
    --document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber":["5432"],"localPortNumber":["15432"]}'
# → Connect: psql -h localhost -p 15432 -U admin -d mydb

# Session logging: CloudWatch Logs or S3 (configure in Session Manager preferences).
# Logs: who connected, when, commands run (with shell integration).
```

### Session Manager vs SSH

| Feature | SSH (key pair) | EC2 Instance Connect | SSM Session Manager |
|:--------|:--------------:|:--------------------:|:-------------------:|
| **Public IP required** | Yes (or bastion) | Yes (or bastion) | No |
| **SSH port open** | Yes | Yes (temporarily) | No |
| **Key management** | PEM file | IAM policy | IAM role |
| **Audit trail** | None | CloudTrail | CloudTrail + Session logs |
| **Cross-account** | Complex | Complex | Native (assume role) |
| **Port forwarding** | Easy | Requires SSH | Built-in |

---

## SSH over Session Manager

> [!info] SSH across SSM
> SSM can act as an SSH proxy. No SSH port needed, no public IP. The SSM Agent handles the SSH connection through the SSM data channel.

```bash
# 1. Register SSM as an SSH proxy:
# Add to ~/.ssh/config:
# host i-* mi-*
#    ProxyCommand aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'

# Alternative SSH tunneling:
aws ssm start-session \
    --target i-1234567890abcdef0 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["my-cluster.cluster-xxx.us-east-1.rds.amazonaws.com"],"portNumber":["3306"],"localPortNumber":["3306"]}'
# → Connect directly to RDS through the SSM tunnel without exposing the DB port.
```

---

## Comparison and Decision Guide

```text
When to use each:
  SSH keys: simple, one-time access to public instances. Not recommended for production.
  Bastion host: controlled access, can run custom tools (IDS, session recording). Complex to operate.
  EC2 Instance Connect: better auditability than SSH keys, but still requires SSH port open.
  SSM Session Manager: RECOMMENDED for production. No SSH ports, full audit trail, no public IP needed.

Default policy: SSM for all automated/managed access. EC2 Instance Connect for emergency break-glass.
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/03_VPC_Subnets_Routes_SGs_NACLs]] for VPC endpoints for SSM
- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for EC2 instance setup with SSM Agent
- [[CICD/AWS/04_Playbooks/05_Debug_EC2_and_SSM]] for SSM/SSH troubleshooting
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for session logging to CloudWatch
