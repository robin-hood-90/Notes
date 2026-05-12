---
tags: [aws, core, kms, secrets-manager, parameter-store, key-policy, envelope-encryption, rotation, vault]
aliases: ["KMS Deep Dive", "Secrets Manager", "Parameter Store", "Key Policies", "Envelope Encryption", "Secret Rotation"]
status: stable
updated: 2026-05-11
---

# KMS and Secrets Manager

> [!summary] Goal
> Master AWS KMS (key management, key policies, auto rotation, envelope encryption, multi-Region keys, and CloudHSM) and AWS Secrets Manager (secret storage, rotation with Lambda, cross-account access) plus Parameter Store (standard vs advanced tiers, parameter policies).

## Table of Contents

1. [KMS — Key Management Service](#kms-key-management-service)
2. [Secrets Manager](#secrets-manager)
3. [Parameter Store](#parameter-store)

---

## KMS — Key Management Service

> [!info] KMS
> KMS manages encryption keys for AWS services and custom applications. It provides FIPS 140-2 validated HSM-backed key storage. Key types: **AWS managed** (created by AWS service), **Customer managed** (you create and control), **Custom key store** (CloudHSM-backed).

### Key policies

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:role/Admin"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:role/AppRole"
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey*"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": { "kms:EncryptionContext:service": "my-app" }
            }
        }
    ]
}
```

### Envelope encryption

```text
KMS does NOT encrypt large data. It encrypts a Data Key (DEK) which is then used to encrypt the data.
  1. GenerateDataKey → returns Plaintext DEK + Encrypted DEK.
  2. Encrypt data with Plaintext DEK (locally, in memory).
  3. Discard Plaintext DEK; store Encrypted DEK alongside the data.
  4. Decrypt: retrieve Encrypted DEK, call Decrypt on KMS → get Plaintext DEK → decrypt data.

  Encryption context: key-value pairs that are cryptographically bound to the DEK.
  The same context is required for decryption.
```

### Multi-Region keys (MRK)

```text
Multi-Region keys are replicated across regions:
  - Primary key in one region → replica keys in other regions.
  - Replicas have the same key ID but separate backings.
  - Can encrypt in one region and decrypt in another.
  - Used by: DynamoDB Global Tables, S3 replication, Kinesis multi-region.

Key states: Enabled, Disabled, PendingDeletion (min 7 days).
Rotation: automatic (1 year for customer managed), or manual with new key creation.
```

---

## Secrets Manager

> [!info] Secrets Manager
> Secrets Manager securely stores, rotates, and retrieves database credentials, API keys, and other secrets. Integrated with RDS, Redshift, DocumentDB. Rotates automatically via Lambda rotation function.

```bash
# Create a secret (RDS rotation):
aws secretsmanager create-secret \
    --name prod/db/password \
    --description "Production DB password" \
    --secret-string '{"username":"admin","password":"$(openssl rand -base64 32)"}' \
    --tags Key=Environment,Value=prod

# Retrieve in code:
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/db/password')
creds = json.loads(secret['SecretString'])
```

### Secret rotation

```text
Rotation stages:
  1. AWSPENDING: new version created (Lambda creates new credentials).
  2. AWSCURRENT: lambda tests new credentials; if works, marks as current.
  3. AWSPREVIOUS: old version retained for rollback.
  4. AWSPENDING is removed (all versions pointing to the rotating secret).

Rotation Lambda: run in VPC (to reach the database).
Schedule: every 30 days by default (configurable cron expression).

Cross-account access: resource-based policy on the secret grants read access to other accounts.
```

---

## Parameter Store

| Tier | Max params | Max size | Cost | Policies |
|:-----|:----------:|:--------:|:----:|:--------:|
| **Standard** | 10,000 | 4KB | Free | No |
| **Advanced** | 100,000 | 8KB | Per param/month | Yes (expiration, notification) |

```bash
# Parameter Store hierarchy:
/prod/db/host
/prod/db/port
/prod/app/config

# SecureString (encrypted with KMS):
aws ssm put-parameter \
    --name /prod/db/password \
    --type SecureString \
    --value "super-secret-password" \
    --key-id "alias/aws/ssm"
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/04_S3_Storage_Policies_Encryption_Lifecycle]] for SSE-KMS with S3
- [[CICD/AWS/01_Foundations/05_RDS_and_Aurora]] for RDS encryption with KMS
- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS secrets injection
- [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] for KMS in compliance frameworks
