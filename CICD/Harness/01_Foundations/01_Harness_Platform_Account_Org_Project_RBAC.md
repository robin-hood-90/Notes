---
tags: [harness, foundations, platform, account, org, project, rbac, governance, sso, audit, opa]
aliases: ["Harness Platform", "Harness RBAC", "Harness Governance", "Harness Variables", "Harness Account Org Project"]
status: stable
updated: 2026-05-11
---

# Harness Platform — Accounts, Orgs, Projects, and RBAC

> [!summary] Goal
> Master the Harness platform hierarchy: Account → Organization → Project. Understand RBAC (resource groups, roles, user groups), SSO/SAML/SCIM, audit trail, governance policies (OPA/Rego), Harness variables (`<+...>` expressions), and built-in pipeline variables.

## Table of Contents

1. [Account → Org → Project Hierarchy](#account-org-project-hierarchy)
2. [RBAC — Resource Groups, Roles, and User Groups](#rbac-resource-groups-roles-and-user-groups)
3. [SSO, SAML, LDAP, and SCIM](#sso-saml-ldap-and-scim)
4. [Harness Variables and Expressions](#harness-variables-and-expressions)
5. [OPA Governance Policies](#opa-governance-policies)

---

## Account → Org → Project Hierarchy

> [!info] Harness hierarchy
> Resources in Harness are organized at three scopes: **Account** (top-level, organization-wide settings, connectors, delegates), **Organization** (group of related projects, teams share connectors/secrets), **Project** (individual service, pipeline, environment). The access of a resource is determined by its scope — a secret at account scope is accessible by all orgs and projects.

```
Account "my-company"
├── Organization "platform-eng"
│   ├── Project "payment-service"
│   │   ├── Pipeline: ci-build
│   │   ├── Service: payment-service
│   │   ├── Environment: production
│   │   └── Connector: payment-k8s
│   └── Project "notification-service"
├── Organization "security"
└── Organization "data-platform"
```

### Resource scope behavior

```yaml
# A secret at Account scope is accessible by ALL projects.
# A secret at Project scope is ONLY accessible by that project.

# Pipeline YAML referencing secrets at different scopes:
secrets:
  - name: db_password               # Project scope
  - name: org_github_token          # Org scope (<+org.secrets.getValue("token")>)
  - name: account_aws_key            # Account scope (<+account.secrets.getValue("key")>)
```

---

## RBAC — Resource Groups, Roles, and User Groups

> [!info] RBAC
> Harness uses a tri-part RBAC model: **User Groups** hold users; **Roles** define permissions (e.g., `Pipeline Executor`, `Deployer`); **Resource Groups** define which resources (pipelines, environments, etc.) are governed. Users get permissions via: `User Group → Role Binding (Role + Resource Group)`.

### Default roles

| Role | Permissions |
|:-----|:------------|
| **Account Admin** | Full access to all account, org, project resources |
| **Organization Admin** | Full access within an organization |
| **Project Admin** | Full access within a project |
| **Pipeline Executor** | Execute pipelines, view pipeline execution history |
| **Deployer** | Deploy services to environments |
| **Developer** | Edit services, environments, pipelines |
| **Viewer** | Read-only access |

### Resource group example

```yaml
resourceGroup:
  name: "payment-team-resources"
  identifier: payment_team_resources
  accountLevelResourceFilters:
    - resourceType: PIPELINE
      identifiers: ["payment-service-ci", "payment-service-cd"]
    - resourceType: ENVIRONMENT
      attributeFilter: "env_type:prod"   # Only production environments
    - resourceType: DELEGATE
      attributeFilter: "selector:payment*"
```

### RBAC inheritance (ACLs)

```text
Permissions are evaluated hierarchically:
  1. Account-level roles apply across ALL orgs and projects.
  2. Org-level roles apply across ALL projects in that org.
  3. Project-level roles apply only to that project.
  4. Pipeline-level default roles (pipeline executor) are auto-created.

If a user is in MULTIPLE user groups with overlapping permissions:
  → The MOST PERMISSIVE rule wins (union of permissions).

Service accounts: non-human identities used for API access.
  Steps:
    Account Settings → Access Control → Service Accounts → + New Service Account
    → Assign Role Binding (e.g., "Pipeline Executor" on CI/CD Pipelines)
    → Generate API Key → Use in CI/CD `HARNESS_API_KEY` for pipeline trigger.

API key types:
  - Personal Access Token (PAT) — per user, for APIs.
  - Service Account Token (SAT) — for automation, machine-to-machine.
```

---

## SSO, SAML, LDAP, and SCIM

> [!info] SSO configuration
> Harness supports SAML 2.0, LDAP, and OAuth (Google, GitHub, Bitbucket) for authentication. SCIM (System for Cross-domain Identity Management) automatically syncs users and groups from your IdP (Okta, Azure AD, OneLogin) to Harness.

```text
Configuration path: Account Settings → Authentication → SSO Providers → + Add SAML

SAML metadata XML upload:
  1. Download metadata XML from IdP (Okta, Azure AD, OneLogin).
  2. Upload to Harness.
  3. Map IdP attributes (email, first name, last name) to Harness user fields.
  4. Enable "Auto provision users from SAML assertions" (creates users on first login).

LDAP:
  Configure LDAP server URL, bind DN, bind password, search base.
  Harness queries LDAP for user/group membership.

SCIM:
  Use SCIM connector to automatically sync user groups from Okta/Azure AD.
  Sync interval: every 1 hour (configurable).
```

---

## Harness Variables and Expressions

> [!info] Harness expressions
> Harness uses `<+...>` syntax for JEXL (Java Expression Language) expressions. Used for: referencing artifact/image tags, stage output variables, pipeline variables, secret references, trigger payloads, and runtime inputs. All pipeline configurations can use expressions.

### Expression categories

```yaml
# Pipeline & Stage identities:
<+pipeline.name>              # Pipeline display name
<+pipeline.identifier>        # Pipeline identifier
<+pipeline.sequenceId>        # Monotonically increasing number (1, 2, 3...)
<+pipeline.executionUrl>      # Link to execution in Harness UI
<+pipeline.startTs>           # Pipeline start timestamp (epoch ms)
<+stage.name>                 # Current stage display name
<+step.name>                  # Current step display name

# Service and Infrastructure:
<+service.name>               # Service name in current stage
<+service.manifest.NAME>            # Manifest content for a given manifest
<+service.manifest.NAME.valuesYaml} # Values YAML content (Helm)
<+artifacts.primary.image>    # Fully qualified artifact image tag
<+artifacts.primary.tag>      # Artifact tag only
<+infra.namespace>             # Deploy namespace (K8s)
<+infra.infraKey>              # Infrastructure identifier

# Trigger payloads:
<+trigger.type>               # "ARTIFACT", "WEBHOOK", "SCHEDULED"
<+trigger.artifact.build>     # Artifact build number/ tag (for artifact trigger)
<+trigger.webhook.git.event>  # "pull_request", "push", etc.
<+trigger.webhook.gitUser>    # User who triggered webhook
<+trigger.webhook.payload.pr.number>  # PR number (GitHub webhook)

# Execution status:
<+currentStep.name>           # Name of the step that produced the output
<+execution.status>           # Pipeline execution status (SUCCESS, FAILED)
<+stage.status>               # Current stage status

# Runtime inputs:
# Pipeline-level variable:
  variables:
    - name: environment
      type: String
      value: dev                 # Default can be overridden at runtime
    - name: deploy_version
      type: String
      value: <+input>            # Must be provided at runtime (blank default)

# Conditional execution:
stage:
  name: Deploy To Prod
  identifier: deploy_prod
  when:
    stageStatus: Success
    condition: <+pipeline.variables.environment> == "production"
```

---

## OPA Governance Policies

> [!info] Harness Governance
> Harness Governance uses Open Policy Agent (OPA) with Rego policy language. Policies are evaluated before pipeline execution/connector creation. If a policy is set to `deny`, the pipeline is BLOCKED. If set to `advisory`, the pipeline runs but a warning is logged.

### Sample Rego policies

```rego
// Policy: enforce naming convention for pipelines
package harness

deny[msg] {
  not re_match("^[a-z]+(-[a-z]+)*", input.pipeline.name)
  msg := sprintf("Pipeline name '%s' does not match naming convention (kebab-case)", [input.pipeline.name])
}

// Policy: require at least one manual approval in production deploy
package harness

deny[msg] {
  input.pipeline.name == "deploy-to-production"
  not any_stage_has_approval
  msg := "Production deploy pipeline must include a manual approval step"
}

any_stage_has_approval {
  input.pipeline.stages[i].spec.execution.steps[_].type == "HarnessApproval"
}

// Policy: block connector with public access
package harness

deny[msg] {
  input.connector.type == "DockerConnector"
  input.connector.spec.auth.type == "Anonymous"
  msg := "Anonymous Docker connector not allowed"
}
```

### Policy configuration

```text
Policy setup: Account Settings → Governance → Policy Sets → + New Policy Set
  - Select entity type: Pipeline, Connector, Environment, Secret.
  - Upload Rego file (or inline editor).
  - Dry run vs Enforcement ("Advisory" or "Deny").
  - Apply to specific org/project (or all).

Policy logs: account-level audit trail shows which policy blocked a deployment.
```

---

## Cross-Links

- [[CICD/Harness/01_Foundations/02_Delegates_Installation_Sizing_Operations]] for delegate-wide RBAC
- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline variables
- [[CICD/Harness/02_Core/06_Chaos_Engineering]] for CE experiments in governance
- [[CICD/Harness/05_Playbooks/05_Harness_Governance_OPA_Rules]] for OPA reference
