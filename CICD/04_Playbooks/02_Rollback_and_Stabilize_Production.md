---
tags: [cicd, playbook, rollback, stabilize, incident-response, deployment-failure]
aliases: ["Rollback Playbook", "Stabilize Production", "Incident Recovery"]
status: stable
updated: 2026-05-11
---

# Playbook: Roll Back and Stabilize Production

> [!summary] Goal
> Restore service fast, then reduce the chance of repeating the incident. Follow: stop the bleeding → validate → prevent recurrence.

## 1. Stop the Bleeding

| Deploy type | Fastest rollback | Command |
|:------------|:-----------------|:--------|
| **K8s rolling** | Revert image to previous version | `kubectl set image deployment/app app=my-app:<prev-tag>` |
| **K8s blue/green** | Switch service selector back | `kubectl patch service app -p '{"spec":{"selector":{"version":"blue"}}}'` |
| **ECS rolling** | Set task definition to previous revision | `aws ecs update-service --service app --task-definition app:42` |
| **ECS blue/green** | Swap target group back | `aws deploy stop-deployment` + revert CodeDeploy |
| **Feature flag** | Toggle flag OFF | Code change (no deploy needed) |
| **Lambda** | Publish previous version, point alias to it | `aws lambda update-alias --function-name app --function-version 41` |
| **Helm** | Rollback to previous release revision | `helm rollback my-release 3` |

## 2. Validate Rollback

```bash
# Check deploy status:
kubectl rollout status deployment/app
aws ecs describe-services --cluster prod --services app

# Check health endpoint:
curl -f https://app.example.com/health

# Check error rate (CloudWatch, Datadog, Prometheus):
# Error rate should return to pre-deploy baseline within 2-3 minutes.
```

## 3. Prevent Recurrence

```text
After stabilization:
  1. Identify why the bad build passed CI:
     - Was there a missing test?
     - Was the test coverage insufficient?
     - Was it a manual mistake (wrong tag deployed)?
  2. Add a guardrail:
     - Add smoke test step after deploy.
     - Add canary with metric-based rollback.
     - Add approval gate for production.
     - Add architecture test (contract test).
  3. Document the incident:
     - What was deployed? What broke? How was it detected? How fixed?
     - Timeline: deploy → detection → rollback → stabilized.
     - Action items with owners and due dates.
```

---

## Cross-Links

- [[CICD/02_Core/01_Deployment_Strategies]] for strategy comparison
- [[CICD/Kubernetes/02_Core/01_Deployments_Rollouts_and_Strategies]] for K8s rollbacks
- [[CICD/AWS/02_Core/01_ECS_Deployments_BlueGreen_and_Rolling]] for ECS rollbacks
- [[SystemDesign/02_Core/08_Incident_Response_and_Postmortem]] for incident analysis
