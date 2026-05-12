---
tags: [github, cicd, playbook, repo-settings, infrastructure-as-code]
aliases: ["Repository Settings as Code", "Repo-as-Code", "GitHub API Settings"]
status: stable
updated: 2026-05-03
---

# Playbook: Manage Repository Settings as Code

> [!summary] Goal
> Manage GitHub repository settings — branch protection, labels, merge settings — declaratively using API scripts, Terraform, or Probot settings.

## Table of Contents

1. [Why Settings as Code Matters](#why-settings-as-code-matters)
2. [Branch Protection via API](#branch-protection-via-api)
3. [Repository Settings via API](#repository-settings-via-api)
4. [Labels via API](#labels-via-api)
5. [Automating Repo Creation](#automating-repo-creation)
6. [Pitfalls](#pitfalls)

---

## Why Settings as Code Matters

Manual configuration through the UI is:
- Not reproducible across repos
- Not auditable
- Error-prone (click fatigue)

Settings as code solves this by defining configurations in version-controlled files or scripts.

---

## Branch Protection via API

```bash
#!/bin/bash
# protect-main.sh
REPO="$1"

# Enable branch protection on main
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI / lint", "CI / test", "CI / build"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null
}
EOF
```

### Apply to all repos in an org

```bash
#!/bin/bash
# protect-all-repos.sh
gh api /orgs/MYORG/repos --paginate --jq '.[].name' | while read repo; do
  echo "Protecting $repo..."
  bash protect-main.sh "MYORG/$repo"
done
```

---

## Repository Settings via API

```bash
#!/bin/bash
# configure-repo.sh
REPO="$1"

# Merge settings
gh api repos/$REPO \
  --method PATCH \
  --field allow_merge_commit=false \
  --field allow_squash_merge=true \
  --field allow_rebase_merge=false \
  --field delete_branch_on_merge=true

# Enable vulnerability alerts
gh api repos/$REPO/vulnerability-alerts \
  --method PUT

# Enable automated security fixes
gh api repos/$REPO/automated-security-fixes \
  --method PUT
```

---

## Labels via API

```bash
#!/bin/bash
# setup-labels.sh
REPO="$1"

declare -A LABELS=(
  ["bug"]="d73a4a"
  ["enhancement"]="a2eeef"
  ["documentation"]="0075ca"
  ["security"]="b60205"
  ["critical"]="b60205"
  ["good first issue"]="7057ff"
  ["needs-triage"]="bfd4f2"
  ["blocked"]="000000"
)

for label in "${!LABELS[@]}"; do
  color="${LABELS[$label]}"
  gh api repos/$REPO/labels \
    --method POST \
    --field name="$label" \
    --field color="$color" \
    --field description="" || \
  gh api repos/$REPO/labels/"$(echo $label | sed 's/ /%20/g')" \
    --method PATCH \
    --field color="$color"
done
```

---

## Automating Repo Creation

```bash
#!/bin/bash
# create-repo.sh
NAME="$1"
TEAM="$2"

# Create repo from template
gh repo create "org/$NAME" \
  --template "org/template-repo" \
  --public \
  --clone

# Configure
cd "$NAME"
bash ../scripts/protect-main.sh "org/$NAME"
bash ../scripts/configure-repo.sh "org/$NAME"
bash ../scripts/setup-labels.sh "org/$NAME"

# Add team
gh api "orgs/org/teams/$TEAM/repos/org/$NAME" --method PUT
```

---

## Pitfalls

### API rate limiting

GitHub API has limits (5,000 requests/hour for authenticated, 60/hour for unauthenticated). Batch operations can hit limits.

**Fix**: Use conditional requests (ETags), stagger batch operations.

### Script drift

Scripts only apply once. If someone changes settings via UI, the script is outdated.

**Fix**: Run protection scripts in CI on a schedule, or use Terraform provider for GitHub and treat config as actual infrastructure.

### Terraform GitHub provider

```hcl
resource "github_branch_protection" "main" {
  repository_id = github_repository.repo.id
  pattern       = "main"

  required_status_checks = ["CI / lint", "CI / test"]
  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
  }
}
```

---

## Cross-Links

- [[CICD/GitHub/01_Foundations/02_Reviews_Checks_and_Branch_Protection]] for protection rules
- [[CICD/GitHub/02_Core/02_Issues_Projects_and_Automation]] for label conventions
- [[CICD/Terraform/00_MOC/00_Terraform_MOC]] for Terraform GitHub provider
