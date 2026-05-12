---
tags: [github, cicd, projects, repo-template]
aliases: ["Repo Template Project"]
status: stable
updated: 2026-05-03
---

# Project: Set Up a Repo Template for Teams

> [!summary] Goal
> Create a repository template that sets up PR templates, CODEOWNERS, branch protection, CI, and release conventions — so every new repo starts with a consistent baseline.

## Requirements

1. PR template + issue templates
2. CODEOWNERS with default ownership
3. Branch protection rules on `main`
4. Required status checks from CI
5. Release/tag conventions
6. Workflow for CI on PRs

## Implementation

### `.github/` directory structure

```
.github/
├── CODEOWNERS
├── dependabot.yml
├── PULL_REQUEST_TEMPLATE.md
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml
│   └── feature_request.yml
└── workflows/
    └── ci.yml
```

### CODEOWNERS

```yaml
# .github/CODEOWNERS
* @org/default-team
/.github/ @org/devops-team
```

### CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
```

### Branch protection (API)

```bash
# Via GitHub API (Script this for new repos)
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][0]="CI / lint" \
  --field required_status_checks[contexts][1]="CI / test" \
  --field enforce_admins=true \
  --field required_pull_request_reviews[required_approving_review_count]=1
```

### Creating the template

```
Repo → Settings → Template repository → ☑️
```

New repos created from this template inherit all files.

---

## Cross-Links

- [[CICD/GitHub/01_Foundations/01_Repo_Workflows_and_PRs]] for PR templates
- [[CICD/GitHub/01_Foundations/02_Reviews_Checks_and_Branch_Protection]] for protection rules
- [[CICD/GitHubActions/01_Foundations/01_Workflow_Syntax_and_Triggers]] for workflow syntax
