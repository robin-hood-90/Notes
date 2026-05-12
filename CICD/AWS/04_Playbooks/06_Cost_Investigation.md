---
tags: [aws, playbook, cost, anomaly, budget, right-sizing, reserved-instances, savings-plans, data-transfer]
aliases: ["Cost Investigation", "AWS Cost Troubleshooting", "Right-Sizing", "Anomaly Detection"]
status: stable
updated: 2026-05-11
---

# Playbook: Cost Investigation

> [!summary] Goal
> Investigate cost anomalies and optimize AWS spending: Cost Explorer filtering by service/region/tag, anomaly detection, right-sizing recommendations, Savings Plans/RI utilization, data transfer costs, and Trusted Advisor.

## First Steps

1. **Cost Explorer**: filter by service for the last 7 days → look for sudden increases.
2. **Group by tag**: if tags are applied, see if a specific team/project is driving costs.
3. **Check data transfer**: NAT Gateway, cross-region, Direct Connect, and CloudFront data transfer.
4. **Check orphaned resources**: unattached EBS volumes, unused Elastic IPs, idle load balancers.
5. **Check Spot usage**: using spot for stateless workloads (ECS/EKS/ASG) reduces EC2 cost by 50-90%.
6. **Check Savings Plans coverage**: ensure compute coverage is > 80% for max discount.

---

## Cross-Links

- [[CICD/AWS/03_Advanced/02_Cost_Management_and_Optimization]] for cost management tools
- [[CICD/AWS/01_Foundations/02_EC2_Instances_Storage_and_Networking]] for spot instances
- [[CICD/AWS/02_Core/05_CloudWatch_Logs_Metrics_and_Alarms]] for cost anomaly alarms
