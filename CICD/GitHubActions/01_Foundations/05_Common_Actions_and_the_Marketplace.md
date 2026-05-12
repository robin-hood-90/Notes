---
tags: [github-actions, cicd, foundations, actions, marketplace, setup-actions]
aliases: ["GitHub Actions Marketplace", "Setup Actions", "Common Actions", "Action Versioning"]
status: stable
updated: 2026-05-03
---

# Common Actions and the Marketplace

> [!summary] Goal
> Use the most common GitHub Actions effectively: checkout code, set up language runtimes, cache dependencies, manage containers, and authenticate to cloud providers.

## Table of Contents

1. [The GitHub Marketplace](#the-github-marketplace)
2. [`actions/checkout` Deep Dive](#actions-checkout-deep-dive)
3. [`actions/setup-*` Family](#actions-setup-family)
4. [`actions/cache`](#actions-cache)
5. [`actions/upload-artifact` and `download-artifact`](#actions-upload-artifact-and-download-artifact)
6. [Docker Actions](#docker-actions)
7. [`docker/setup-qemu-action` — Multi-Arch Builds](#docker-setup-qemu-action-multi-arch-builds)
8. [`actions/attest-build-provenance` — Build Attestation](#actions-attest-build-provenance-build-attestation)
9. [Cloud Auth Actions](#cloud-auth-actions)
10. [`github/codeql-action` Deep Dive](#github-codeql-action-deep-dive)
11. [`actions/dependency-review-action`](#actions-dependency-review-action)
12. [Service Containers](#service-containers)
13. [Dependabot for GitHub Actions](#dependabot-for-github-actions)
14. [Notification Actions](#notification-actions)
15. [Action Versioning Best Practices](#action-versioning-best-practices)
16. [Pitfalls](#pitfalls)

---

## The GitHub Marketplace

The [GitHub Marketplace](https://github.com/marketplace?type=actions) hosts thousands of actions. When evaluating actions:

| Criteria | What to check |
|----------|--------------|
| **Publisher** | Verified creator, GitHub official, or community |
| **Stars** | Popularity and community trust |
| **Last updated** | Active maintenance |
| **Version pinned** | SHA pinning, major version tag |
| **License** | Open source or restrictive |

---

## `actions/checkout` Deep Dive

```yaml
- uses: actions/checkout@v4
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `repository` | `github.repository` | Repo to check out |
| `ref` | `github.ref` | Branch/tag/commit to check out |
| `fetch-depth` | `1` | Number of commits to fetch. `0` = full history |
| `persist-credentials` | `true` | Save token for git commands |
| `path` | `github.workspace` | Relative path to place the repo |
| `sparse-checkout` | — | Only checkout specific paths |
| `lfs` | `false` | Download Git LFS files |
| `submodules` | `false` | Recursively clone submodules |

```yaml
# Full git history (needed for monorepo tools)
- uses: actions/checkout@v4
  with:
    fetch-depth: 0

# Sparse checkout — only specific directory
- uses: actions/checkout@v4
  with:
    sparse-checkout: |
      src
      package.json

# Checkout a different repository
- uses: actions/checkout@v4
  with:
    repository: org/another-repo
    token: ${{ secrets.PAT }}
    path: vendor/another-repo
```

---

## `actions/setup-*` Family

### `setup-node`

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm                 # auto-cache ~/.npm
    registry-url: https://npm.pkg.github.com
    scope: "@my-org"
```

| Parameter | Options |
|-----------|---------|
| `node-version` | `18`, `20`, `22`, `lts/*`, `latest` |
| `cache` | `npm`, `yarn`, `pnpm`, or empty |
| `registry-url` | npm registry URL |
| `scope` | npm scope for private packages |

### `setup-python`

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip
```

| Parameter | Options |
|-----------|---------|
| `python-version` | `"3.10"`, `"3.12"`, `"pypy3.10"` |
| `cache` | `pip`, `pipenv`, `poetry` |

### `setup-java`

```yaml
- uses: actions/setup-java@v4
  with:
    java-version: 21
    distribution: temurin
    cache: maven
```

| Distribution | Provider |
|-------------|----------|
| `temurin` | Eclipse Adoptium (recommended) |
| `zulu` | Azul |
| `adopt` | Legacy |
| `corretto` | AWS |
| `microsoft` | Microsoft |

### `setup-go`

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: "1.22"
    cache: true
```

---

## `actions/cache`

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      npm-${{ runner.os }}-
    lookup-only: false
```

| Parameter | Description |
|-----------|-------------|
| `path` | File(s) to cache (glob patterns) |
| `key` | Unique cache identifier (required) |
| `restore-keys` | Fallback keys if exact match fails |
| `lookup-only` | Check key exists without restoring |

---

## `actions/upload-artifact` and `download-artifact`

### Upload

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: dist-files
    path: dist/
    retention-days: 30
    overwrite: true
    if-no-files-found: warn     # or: error, ignore
```

### Download

```yaml
- uses: actions/download-artifact@v4
  with:
    name: dist-files
    path: ./build
```

---

## Docker Actions

### Docker login

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Docker build and push

```yaml
- uses: docker/setup-buildx-action@v3       # Sets up BuildKit builder

- uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha      # GitHub Actions cache
    cache-to: type=gha,mode=max
    platforms: linux/amd64,linux/arm64   # multi-arch
    sbom: true                            # generate SBOM
    provenance: true                      # attestation
```

```mermaid
flowchart LR
    A[Dockerfile] --> B[docker/setup-buildx-action]
    B --> C[docker/build-push-action]
    C --> D[Build image]
    D --> E[Cache to GHA cache]
    D --> F[Push to registry]
    D --> G[Generate SBOM + provenance]
```

---

## Cloud Auth Actions

### AWS

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456:role/github-actions
    aws-region: us-east-1
    role-session-name: github-actions-${{ github.run_id }}
```

### GCP

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/my-pool/providers/my-provider
    service_account: my-sa@my-project.iam.gserviceaccount.com
```

### Azure

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

---

## `github/codeql-action`

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: javascript,typescript
    queries: security-and-quality

- uses: github/codeql-action/autobuild@v3

- uses: github/codeql-action/analyze@v3
  with:
    category: "/language:javascript-typescript"
```

---

## Action Versioning Best Practices

| Method | Example | Trust level | Stability |
|--------|---------|-------------|-----------|
| Major version | `@v4` | Moderate | Points to latest v4.x |
| Minor + major | `@v4.2` | Moderate | Points to v4.2.x |
| Full SHA | `@e4f7c9a` | High | Immutable — won't change |
| Commit branch | `@main` | Low | Breaks at any time |

```yaml
# RECOMMENDED: Pin major version for workflow actions
- uses: actions/checkout@v4

# RECOMMENDED: Pin SHA for critical third-party actions
- uses: some-org/security-action@e4f7c9a...

# AVOID: Branch references
- uses: actions/checkout@main  # unstable!
```

### Dependabot for actions

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: weekly
```

---

## `docker/setup-qemu-action` — Multi-Arch Builds

Builds Docker images for multiple architectures (amd64, arm64, armv7) using QEMU emulation:

```yaml
- uses: docker/setup-qemu-action@v3
  with:
    platforms: linux/amd64,linux/arm64,linux/arm/v7

- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64,linux/arm/v7
    push: true
    tags: ${{ vars.REGISTRY }}/my-app:latest
```

```mermaid
flowchart LR
    A[Dockerfile] --> B[setup-qemu-action: register emulators]
    B --> C[setup-buildx: create multi-arch builder]
    C --> D[build-push for linux/amd64]
    C --> E[build-push for linux/arm64]
    C --> F[build-push for linux/arm/v7]
    D --> G[Manifest list: single tag, multiple arches]
    E --> G
    F --> G
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `platforms` | Comma-separated platforms to support | `linux/amd64` |
| `image` | QEMU static binary image | `tonistiigi/binfmt:latest` |

---

## `actions/attest-build-provenance` — Build Attestation

Generates cryptographically signed attestations for build artifacts, proving where, when, and how they were built.

```yaml
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: dist/app.tar.gz
```

### Verification

```bash
# Verify an artifact
gh attestation verify dist/app.tar.gz --repo owner/repo

# Output includes:
# - Repository and workflow
# - Commit SHA
# - Builder identity
```

---

## `github/codeql-action` Deep Dive

### Parameters

| Parameter | `init` | `autobuild` | `analyze` |
|-----------|--------|-------------|-----------|
| `languages` | `javascript,python,java,...` | — | — |
| `queries` | `security-and-quality`, `security-extended` | — | — |
| `config-file` | Path to custom config | — | — |
| `source-root` | Source root directory | — | — |
| `category` | — | — | `"/language:javascript"` |
| `upload` | — | — | `true`/`false` |
| `ram` | — | — | Memory limit in MB |

### Custom CodeQL configuration

```yaml
# .github/codeql/codeql-config.yml
name: "Custom CodeQL config"
queries:
  - uses: security-and-quality
paths-ignore:
  - node_modules
  - "**/*.test.js"
```

### Full workflow

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: javascript,python
    queries: security-and-quality
    config-file: .github/codeql/codeql-config.yml
- uses: github/codeql-action/autobuild@v3
- uses: github/codeql-action/analyze@v3
  with:
    category: "/language:javascript"
```

---

## `actions/dependency-review-action`

Analyzes dependency changes in PRs, flagging known vulnerabilities and license issues:

```yaml
- uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high
    deny-licenses: GPL-3.0, AGPL-3.0
    allow-licenses: MIT, Apache-2.0, BSD-3
    comment-summary-in-pr: true
```

---

## Service Containers

Run supporting services (databases, caches) in separate containers during a job:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/postgres
          REDIS_URL: redis://localhost:6379
```

| Option | Description |
|--------|-------------|
| `image` | Docker image for the service |
| `env` | Environment variables |
| `ports` | Port mapping (host:container) |
| `volumes` | Volume mounting |
| `options` | Additional Docker run options (health checks, capabilities) |
| `credentials` | Docker registry credentials for private images |

---

## Dependabot for GitHub Actions

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: weekly
      day: monday
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "my-team"
    labels:
      - "dependencies"
      - "github-actions"
    allow:
      - dependency-type: "all"
```

| Option | Description |
|--------|-------------|
| `package-ecosystem` | Must be `"github-actions"` for Actions |
| `directory` | `"/"` for `.github/workflows/` |
| `schedule.interval` | `daily`, `weekly`, `monthly` |
| `open-pull-requests-limit` | Max open Dependabot PRs |
| `reviewers` | Auto-requested reviewers |
| `labels` | Labels for Dependabot PRs |
| `allow` | Filter by dependency type |

---

## Notification Actions

### Slack

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "Workflow ${{ github.workflow }} failed on ${{ github.repository }}"}
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### GitHub Script (custom comments, issues)

```yaml
- name: Comment on PR
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: 'CI checks passed!'
      })
```

### Choosing a notification action

```mermaid
flowchart TD
    A[Need to notify?] --> B{Platform}
    B -->|Slack| C[slackapi/slack-github-action]
    B -->|Email| D[Custom: actions/github-script + SMTP]
    B -->|GitHub| E[actions/github-script for comments/issues]
    B -->|Teams| F[Action: microsoft/teams-notification]
    B -->|Discord| G[Action: Ilshidur/action-discord]
    B -->|PagerDuty| H[Action: PagerDuty/incident-workflow]
```

### Not pinning action versions

Using `@main` or `@v4` without a lock breaks when maintainers push breaking changes to the same major version.

**Fix**: Dependabot updates pinned versions. Use major version tags for well-maintained official actions.

### Using unmaintained actions

Actions that haven't been updated in 2+ years may have security vulnerabilities.

**Fix**: Check last update date. Prefer GitHub-official actions.

### `pull_request_target` + unsafe checkout

Running `actions/checkout` in a `pull_request_target` workflow checks out the PR head with full access to base repo secrets.

**Fix**: Never run untrusted PR code in `pull_request_target`. Only use for labeling/commenting.

### Misconfigured `docker/login-action`

```yaml
# FAILS: wrong registry URL format
docker/login-action@v3
  registry: ghcr  # missing .io
```

**Fix**: Use `ghcr.io`, `docker.io`, or `my-registry.azurecr.io`.

---

> [!question]- Interview Questions
>
> **Q: How do you pin action versions safely?**
> A: Use major version tags (`@v4`) for trusted first-party actions. Use full SHA (`@e4f7c9a`) for third-party actions. Use Dependabot to update them automatically.
>
> **Q: What is the `docker/build-push-action` used for?**
> A: It builds a Docker image using BuildKit and can push to any container registry. Supports caching, multi-arch builds, SBOM generation, and provenance attestation.
>
> **Q: How do you authenticate to AWS in a workflow without static keys?**
> A: Use `aws-actions/configure-aws-credentials` with OIDC: `role-to-assume` expects an IAM role ARN, and the workflow needs `permissions: id-token: write`.

---

## Cross-Links

- [[CICD/GitHubActions/01_Foundations/03_Caching_and_Matrix_Builds]] for cache action details
- [[CICD/GitHubActions/02_Core/01_Secrets_Environments_and_OIDC]] for OIDC auth
- [[CICD/GitHubActions/01_Foundations/01_Workflow_Syntax_and_Triggers]] for trigger context

---

## References

- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [actions/checkout](https://github.com/actions/checkout)
- [actions/setup-node](https://github.com/actions/setup-node)
- [docker/build-push-action](https://github.com/docker/build-push-action)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [GitHub CodeQL Action](https://github.com/github/codeql-action)
