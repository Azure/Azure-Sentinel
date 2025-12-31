# Red Canary

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Red Canary |
| **Support Tier** | Partner |
| **Support Link** | [https://www.redcanary.com](https://www.redcanary.com) |
| **Categories** | domains |
| **First Published** | 2022-03-04 |
| **Last Updated** | 2022-03-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Red Canary Threat Detection](../connectors/redcanarydataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`RedCanaryDetections_CL`](../tables/redcanarydetections-cl.md) | [Red Canary Threat Detection](../connectors/redcanarydataconnector.md) | Analytics |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Red Canary Threat Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary/Analytic%20Rules/RedCanaryThreatDetection.yaml) | High | Collection, CommandAndControl, CredentialAccess, DefenseEvasion, Discovery, Execution, Exfiltration, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`RedCanaryDetections_CL`](../tables/redcanarydetections-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
