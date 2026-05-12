---
tags: [aws, playbook, ec2, ssh, ssm, connection-refused, user-data, cloud-init, serial-console]
aliases: ["Debug EC2", "Debug SSM Agent", "EC2 SSH Troubleshooting", "User Data Debug"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug EC2 and SSM

> [!summary] Goal
> Diagnose EC2 SSH/SSM connectivity issues: SSH connection refused (SG, key pair, user), SSM agent not connecting (VPC endpoints, IAM, agent status), user data scripts failing (cloud init logs), and using the serial console for boot-level debugging.

## SSH Connection Refused

| Cause | Check |
|:------|:------|
| Wrong user | `ec2-user`, `ubuntu`, `admin` depending on AMI |
| Security group no port 22 | Check SG inbound rules |
| NACL blocking | NACLs are stateless — ensure ephemeral ports allowed for return traffic |
| Key pair mismatch | Wrong `.pem` or `authorized_keys` has wrong public key |
| Instance not running | `DescribeInstanceStatus`, instance health checks |

---

## Cross-Links

- [[CICD/AWS/03_Advanced/03_SSM_Session_Manager_and_SSH]] for SSM/SSH connectivity
- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for EC2 instance types
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for CloudWatch Agent
