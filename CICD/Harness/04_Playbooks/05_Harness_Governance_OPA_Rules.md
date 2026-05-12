---
tags: [harness, playbook, opa, rego, governance, policy-deny, advisory, pipeline-blocked]
aliases: ["Harness OPA Governance", "Policy Denied Pipeline", "Rego Troubleshooting"]
status: stable
updated: 2026-05-11
---

# Playbook: Harness Governance OPA Rules

> [!summary] Goal
> Diagnose OPA policy failures: pipeline blocked by policy, policy not evaluated, `deny` output shown, OPA dry-run vs enforcement, and writing effective Rego rules for Harness entities.

| Symptom | Cause | Check | Fix |
|:--------|:------|:------|:-----|
| Pipeline blocked: `blocked_by_policy` | OPA rule denied the pipeline | `pipeline execution logs` → denied rule name | Update pipeline to comply or modify OPA rule |
| OPA not evaluated | Policy set not assigned to entity type | Policy set → Entity type → Pipeline connector/environment/secret | Assign policy set to "Pipeline" entity |
| Dry-run shows no error but enforcement blocks | Policy set in "Advisory" mode only logs | Check OPA logs for dry-run warnings | Change to "Deny" mode if that's the intent |
| Rego rule not applied to all pipelines | Policy scope is account, but pipeline is in project | Check policy set → org/project scoping | Widen scope to "ALL" or add specific org/project |

---

## Cross-Links

- [[CICD/Harness/01_Foundations/01_Harness_Platform_Account_Org_Project_RBAC]] for governance policies
- [[CICD/Harness/03_Advanced/05_Pipelines_as_YAML_Complete_Reference]] for expression reference
- [[CICD/Harness/01_Foundations/06_Pipelines_Stages_Steps_and_Execution_Flow]] for pipeline structure
