---
tags: [aws, playbook, iam, access-denied, cloudtrail, policy-simulator, access-analyzer]
aliases: ["Debug IAM AccessDenied", "IAM Troubleshooting", "Access Denied Debug"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug IAM AccessDenied

> [!summary] Goal
> Diagnose and fix IAM AccessDenied errors: decode authorization messages, use the IAM policy simulator, analyze CloudTrail events, check SCPs/permission boundaries, and verify trust policies.

## Step-by-step Triage

1. **Check the error message**: `AccessDenied` errors include a request ID. Use `sts:DecodeAuthorizationMessage` to decode:
   ```bash
   aws sts decode-authorization-message --encoded-message <encoded>
   ```
2. **Check CloudTrail**: search `eventName`, `errorCode=AccessDenied`, `userIdentity.arn`, `sourceIPAddress`.
3. **Run the IAM Policy Simulator**: `aws iam simulate-principal-policy --policy-source-arn arn:... --action-names s3:GetObject`.
4. **Check SCPs** (if in an Organization): look at the management account SCPs that apply to this account/OU.
5. **Check permission boundaries** (if set on the role).
6. **Check trust policy** (cross-account access): the `sts:AssumeRole` trust policy must allow the principal.

---

## Cross-Links

- [[CICD/AWS/01_Foundations/01_IAM_Basics_for_Engineers]] for IAM fundamentals
- [[CICD/AWS/02_Core/09_CloudTrail_Config_and_Compliance]] for CloudTrail analysis
- [[CICD/AWS/03_Advanced/05_Security_Encryption_and_Compliance]] for SCPs
