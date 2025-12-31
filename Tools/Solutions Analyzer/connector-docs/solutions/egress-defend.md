# Egress Defend

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | egress1589289169584 |
| **Support Tier** | Partner |
| **Support Link** | [https://support.egress.com/s/](https://support.egress.com/s/) |
| **Categories** | domains |
| **First Published** | 2023-07-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Egress Defend](../connectors/egressdefendpolling.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`EgressDefend_CL`](../tables/egressdefend-cl.md) | [Egress Defend](../connectors/egressdefendpolling.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Hunting Queries | 1 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Egress Defend - Dangerous Attachment Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Analytic%20Rules/DangerousAttachmentReceived.yaml) | Medium | Execution, InitialAccess, Persistence, PrivilegeEscalation | [`EgressDefend_CL`](../tables/egressdefend-cl.md) |
| [Egress Defend - Dangerous Link Click](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Analytic%20Rules/DangerousLinksClicked.yaml) | Medium | Execution | [`EgressDefend_CL`](../tables/egressdefend-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Dangerous emails with links clicked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Hunting%20Queries/DangerousLinksClicked.yaml) | Collection | [`EgressDefend_CL`](../tables/egressdefend-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DefendMetrics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Workbooks/DefendMetrics.json) | [`EgressDefend_CL`](../tables/egressdefend-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DefendAuditData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Defend/Parsers/DefendAuditData.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 02-08-2023                     | Initial Solution Release.                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
