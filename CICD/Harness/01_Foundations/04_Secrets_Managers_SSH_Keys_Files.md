---
tags: [harness, foundations, secrets, vault, aws-secrets, gcp-secrets, ssh-key, encrypted-file]
aliases: ["Harness Secrets", "Secret Manager", "Vault Connector", "AWS Secrets Manager", "SSH Key", "Encrypted File"]
status: stable
updated: 2026-05-11
---

# Secrets Management — Secret Managers, SSH Keys, and Files

> [!summary] Goal
> Master Harness secrets management: built-in vs third-party secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault), SSH key secrets, encrypted files, secret referencing expressions, and secret scope (Account/Org/Project).

## Table of Contents

1. [Secret Managers](#secret-managers)
2. [Secret Types and References](#secret-types-and-references)
3. [SSH Key Secrets and Encrypted Files](#ssh-key-secrets-and-encrypted-files)

---

## Secret Managers

> [!info] Secret manager
> A secret manager stores secrets in encrypted form. Harness supports: built-in secret manager (encrypted at rest within Harness), HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault. The built-in manager is free and sufficient for most cases. Vault is the most popular third-party option.

### Built-in secret manager

```text
Harness encrypts secrets at rest using its built-in encryption provider.
Best for: teams without an existing secrets infrastructure.
Limitations: doesn't support auto-rotation, replication across regions requires migration.

Setup:
  Account Settings → Secrets Management → Secret Managers → + Add Secret Manager
  → "Harness Built-in Secret Manager" (pre-configured, no setup needed).
```

### HashiCorp Vault connector

```yaml
# Vault connector YAML:
connector:
  name: "vault-prod"
  identifier: vault_prod
  type: Vault
  spec:
    vaultUrl: "https://vault.mycompany.com:8200"
    authTokenRef: account.vault_auth_token   # Secret referencing Vault token
    basePath: "harness"
    namespace: "admin"
    readOnly: false        # Harness can also create/update secrets in Vault
    renewalIntervalMinutes: 60   # Token renewal interval
    default: true          # Harness will create new secrets in Vault by default
    delegateSelectors:
      - team:platform
```

### AWS Secrets Manager connector

```yaml
connector:
  name: "aws-secrets-manager"
  identifier: aws_secrets_manager
  type: AwsSecretManager
  spec:
    region: "us-east-1"
    secretNamePrefix: "/harness/"
    credentials:
      type: ManualConfig
      spec:
        accessKey: "AKIAIOSFODNN7EXAMPLE"
        secretKeyRef: account.aws_secret_key
    delegateSelectors:
      - env:prod
```

---

## Secret Types and References

> [!info] Secret reference
> Secrets are referenced using `<+secrets.getValue("secret_identifier")>` in pipeline YAML and connector fields. Secrets looked up first at project scope, then org, then account. The resolved value is never shown in logs (masked as `[HARNESS_SECRET]`).

### Secret types

| Secret type | Contents | Max size | Use case |
|:------------|:--------:|:--------:|----------|
| **Text** | String (password, token, API key) | 50 KB | Passwords, PAT tokens, API keys |
| **File** | Binary file (PEM, PKCS12) | 10 MB | Certificates, SSH keys, credential files |
| **SSH Key** | SSH private key + passphrase | 50 KB | Git SSH authentication |

### Creating secrets

```text
[Image: Harness UI → Project Setup → Secrets → + New Secret → Text]

Steps to create a text secret:
  1. Navigate to Project Setup → Secrets.
  2. Click "New Secret" → "Text".
  3. Name: "db_password", value: "super-secret".
  4. Secret Manager: Harness built-in (or Vault/AWS/etc.)
  5. Scope: Project (or Org/Account).
  6. Save.

Usage in pipeline YAML:
steps:
  - step:
      type: ShellScript
      spec:
        source:
          type: Inline
          spec:
            script: |
              echo "Connecting to DB with password: <+secrets.getValue("db_password")>"
              # At runtime, this renders as [HARNESS_SECRET] in logs
```

---

## SSH Key Secrets and Encrypted Files

### SSH key secrets

```yaml
# SSH key secret for Git connectors:
secrets:
  - type: SSHKey
    spec:
      key:
        type: KeyReference
        spec:
          secret: account.my_ssh_private_key    # Reference to text secret containing PEM
      passphrase:                                # Optional passphrase
        type: Encrypted
        spec:
          secret: account.ssh_passphrase
```

### Encrypted files

```yaml
# Encrypted file secret (e.g., Google service account JSON):
secrets:
  - type: SecretFile
    spec:
      secretManager: account.harnessSecretManager
      secret: account.gcp_sa_key_file   # File binary (.json, .p12)
```

### Scope and Access

```yaml
# Referencing secrets across scopes:
secrets:
  - name: db_password               # Project scope (implicit)
  - name: org_GitHub_TOKEN           # Org scope:
    identifier: org_token
    value: <+org.secrets.getValue("org_token")>

  # Account scope for API token shared by all projects:
  # setup as text secret @ Account level.
  # Pipeline references as:
  #   <+account.secrets.getValue("account_aws_key")>
```

### Secrets in environment variables

```yaml
# Mapping secrets to environment variables in a Shell Script step:
- step:
    type: ShellScript
    spec:
      environmentVariables:
        - name: DB_PASSWORD
          type: String
          value: <+secrets.getValue("db_password")>
        - name: API_TOKEN
          type: String
          value: <+account.secrets.getValue("account_github_token")>
      script: |
        curl -H "Authorization: Bearer $API_TOKEN" https://api.github.com
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/03_Connectors_Cloud_Providers_Repos_and_Tools]] for secret references in connectors
- [[CICD/Harness/01_Foundations/01_Harness_Platform_Account_Org_Project_RBAC]] for secret scope and RBAC
- [[CICD/Harness/02_Core/05_Feature_Flags_Creation_Targeting_and_SDKs]] for feature flag secrets (SDK keys)
- [[CICD/Harness/05_Projects/01_Full_CD_Pipeline_with_Approvals_Rollback]] for secrets in real pipeline
