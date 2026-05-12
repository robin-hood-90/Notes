---
tags: [jenkins, cicd, foundations, credentials, secrets, vault, withcredentials]
aliases: ["Jenkins Credentials", "Secrets", "withCredentials", "Vault Integration"]
status: stable
updated: 2026-05-03
---

# Credentials and Secrets

> [!summary] Goal
> Use Jenkins credentials safely — understand credential types, injection patterns, and how to integrate with HashiCorp Vault.

## Table of Contents

1. [Why Credentials Matter](#why-credentials-matter)
2. [Credential Types](#credential-types)
3. [`withCredentials` Step](#withcredentials-step)
4. [`credentials()` in Environment](#credentials-in-environment)
5. [HashiCorp Vault Integration](#hashicorp-vault-integration)
6. [Best Practices](#best-practices)
7. [Pitfalls](#pitfalls)

---

## Why Credentials Matter

Jenkins credentials store sensitive values (passwords, tokens, keys) and inject them into pipelines safely — never in SCM, never in logs.

```mermaid
flowchart LR
    A[Jenkins Credential Store] --> B[withCredentials step]
    B --> C[Masked in logs]
    B --> D[Available as environment variable]
    B --> E[Available as file]
    C --> F[Pipeline step uses credential]
    D --> F
    E --> F
```

> [!tip] Definition
> **Credentials**: securely stored secrets managed by Jenkins. They are encrypted at rest, masked in logs, and injected into pipelines via the `withCredentials` step or `credentials()` binding.

---

## Credential Types

| Type | ID prefix | Use case | Example |
|------|-----------|----------|---------|
| **Username with password** | `usernamePassword` | GitHub, Docker Hub, database | `withCredentials([usernamePassword(credentialsId: 'github', usernameVariable: 'USER', passwordVariable: 'PASS')])` |
| **SSH key** | `sshUserPrivateKey` | Git over SSH, remote server access | `withCredentials([sshUserPrivateKey(credentialsId: 'ssh-key', keyFileVariable: 'KEY')])` |
| **Secret text** | `string` | API tokens, webhook secrets | `withCredentials([string(credentialsId: 'slack-token', variable: 'TOKEN')])` |
| **Secret file** | `file` | Service account JSON, certificate | `withCredentials([file(credentialsId: 'gcp-sa', variable: 'SA_FILE')])` |
| **Certificate** | `certificate` | PKCS#12 certificates | `withCredentials([certificate(credentialsId: 'my-cert', keystoreVariable: 'KEYSTORE')])` |
| **Docker credentials** | `docker` | Docker registry auth | Built into `withDockerRegistry` |

---

## `withCredentials` Step

```groovy
// Username/password
withCredentials([
    usernamePassword(
        credentialsId: 'github-token',
        usernameVariable: 'GIT_USER',
        passwordVariable: 'GIT_TOKEN'
    )
]) {
    sh """
        git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/org/repo.git
        git push origin main
    """
}

// SSH key
withCredentials([
    sshUserPrivateKey(
        credentialsId: 'deploy-key',
        keyFileVariable: 'SSH_KEY',
        passphraseVariable: 'SSH_PASS'
    )
]) {
    sh 'ssh -i $SSH_KEY -o StrictHostKeyChecking=no user@host ./deploy.sh'
}

// Secret text (API token)
withCredentials([
    string(credentialsId: 'slack-webhook', variable: 'SLACK_URL')
]) {
    sh "curl -X POST -H 'Content-type: application/json' --data '{\"text\":\"Build done!\"}' \$SLACK_URL"
}

// Secret file (GCP service account JSON)
withCredentials([
    file(credentialsId: 'gcp-service-account', variable: 'GCP_SA_FILE')
]) {
    sh "gcloud auth activate-service-account --key-file=\$GCP_SA_FILE"
}
```

---

## `credentials()` in Environment

Pipelines can bind credentials as environment variables:

```groovy
pipeline {
    environment {
        GITHUB_TOKEN = credentials('github-token')
        DOCKER_CREDS = credentials('docker-hub')
    }
    stages {
        stage('Deploy') {
            steps {
                // GITHUB_TOKEN is injected as environment variable
                // DOCKER_CREDS creates GITHUB_TOKEN_USR and GITHUB_TOKEN_PSW
                sh 'curl -H "Authorization: token $GITHUB_TOKEN" ...'
            }
        }
    }
}
```

```mermaid
flowchart TD
    A[credentials('my-creds')] --> B{Type?}
    B -->|UsernamePassword| C["env.MY_CREDS_USR + env.MY_CREDS_PSW"]
    B -->|Secret text| D["env.MY_CREDS (single value)"]
    B -->|SSH key| E["env.MY_CREDS (key file path)"]
```

---

## HashiCorp Vault Integration

The HashiCorp Vault plugin fetches secrets from Vault at pipeline runtime:

```groovy
// Install: HashiCorp Vault Pipeline Plugin
pipeline {
    environment {
        // Fetch secret from Vault path
        DB_PASSWORD = vault path: 'secret/data/db', key: 'password'
    }
    stages {
        stage('Database') {
            steps {
                withVault(
                    configuration: [
                        vaultUrl: 'https://vault.example.com',
                        vaultCredentialId: 'vault-token',
                        engineVersion: 2
                    ],
                    vaultSecrets: [
                        [
                            path: 'secret/data/production/db',
                            engineVersion: 2,
                            secretValues: [
                                [envVar: 'DB_URL', vaultKey: 'url'],
                                [envVar: 'DB_USER', vaultKey: 'username'],
                                [envVar: 'DB_PASS', vaultKey: 'password']
                            ]
                        ]
                    ]
                ) {
                    sh "connect \$DB_URL \$DB_USER \$DB_PASS"
                }
            }
        }
    }
}
```

```mermaid
sequenceDiagram
    participant P as Pipeline
    participant J as Jenkins
    participant V as Vault Server

    P->>J: vault path: 'secret/data/db'
    J->>V: Request secret with token
    V-->>J: Encrypted response
    J-->>P: Environment variable with value
    P->>P: Use $DB_PASSWORD in steps
```

---

## Best Practices

- [ ] Use the **minimum credential type** — secret text for tokens, usernamePassword for auth pairs
- [ ] **Scope credentials** to folders/projects, not globally
- [ ] **Mask passwords in logs** — Jenkins does this automatically for `withCredentials`
- [ ] **Never echo credentials** — `sh "echo $PASSWORD"` defeats masking
- [ ] **Rotate credentials** regularly — use Vault for dynamic secrets
- [ ] **Use `credentials()` in environment** for simple injection, `withCredentials` for complex scenarios

---

## Pitfalls

### Credentials in build logs

```groovy
// BAD — password echoed to log
sh "echo $PASSWORD"

// BAD — password in URL
sh "git push https://$USER:$PASS@github.com/org/repo.git"

// GOOD — masked by Jenkins
withCredentials([string(credentialsId: 'token', variable: 'TOKEN')]) {
    sh "curl -H 'Authorization: Bearer $TOKEN' https://api.example.com"
}
```

### Credentials as build parameters

```groovy
parameters {
    password(name: 'DB_PASS', defaultValue: '')  // VISIBLE IN BUILD LOG!
}
```

**Fix**: Store in Jenkins credential store and reference by ID, not as a build parameter.

### Baking credentials into images

```groovy
sh 'docker build -t my-app --build-arg API_KEY=$API_KEY .'  // API_KEY in image layer
```

**Fix**: Use BuildKit secrets: `RUN --mount=type=secret,id=api_key ...` or inject at runtime via environment variables.

---

> [!question]- Interview Questions
>
> **Q: What credential types does Jenkins support?**
> A: Username with password, SSH key, Secret text, Secret file, Certificate. Each is injected into pipelines via `withCredentials` or `credentials()`.
>
> **Q: How do you prevent a credential from appearing in logs?**
> A: Jenkins automatically masks values injected via `withCredentials` and `credentials()` in environment. Never `echo` the variable — use it directly in commands.
>
> **Q: How does the Vault plugin work with Jenkins?**
> A: The pipeline specifies a Vault path and key. Jenkins authenticates to Vault (via token, AppRole, or Kubernetes auth) and injects the secret as an environment variable.

---

## Cross-Links

- [[CICD/Jenkins/03_Advanced/02_Configuration_as_Code_JCasC]] for managing credentials via JCasC YAML
- [[CICD/02_Core/02_Secrets_Management]] for organization-wide secrets management
- [[CICD/Jenkins/03_Advanced/03_Security_RBAC]] for credential access control

---

## References

- [Jenkins Credentials](https://www.jenkins.io/doc/book/using/using-credentials/)
- [Credentials Binding Plugin](https://plugins.jenkins.io/credentials-binding/)
- [HashiCorp Vault Plugin](https://plugins.jenkins.io/hashicorp-vault-plugin/)
