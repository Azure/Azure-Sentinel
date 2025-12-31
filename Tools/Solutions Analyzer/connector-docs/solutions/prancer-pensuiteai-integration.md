# Prancer PenSuiteAI Integration

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Prancer PenSuiteAI Integration |
| **Support Tier** | Partner |
| **Support Link** | [https://www.prancer.io](https://www.prancer.io) |
| **Categories** | domains |
| **First Published** | 2023-08-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Prancer Data Connector](../connectors/prancerlogdata.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`prancer_CL`](../tables/prancer-cl.md) | [Prancer Data Connector](../connectors/prancerlogdata.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **14 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Disks Alerts From Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Disks_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Flow Logs Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Flow_Logs_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [NetworkSecurityGroups Alert From Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Network_Security_Groups_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [PAC high severity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/PAC_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Registries Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Registries_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Sites Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Sites_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Storage Accounts Alerts From Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Storage_Accounts_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Subnets Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Subnets_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Vaults Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Vaults_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [Virtual Machines Alerts for Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/VM_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |
| [VirtualNetworkPeerings Alerts From Prancer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Analytic%20Rules/Virtual_Networks_High_Severity.yaml) | High | Reconnaissance | [`prancer_CL`](../tables/prancer-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Hunting Query for Failed CSPM Scan Items](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Hunting%20Queries/CSPM_query.yaml) | Collection | [`prancer_CL`](../tables/prancer-cl.md) |
| [Hunting Query for High Severity PAC findings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Hunting%20Queries/PAC_high_severity_query.yaml) | Collection | [`prancer_CL`](../tables/prancer-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PrancerSentinelAnalytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Prancer%20PenSuiteAI%20Integration/Workbooks/PrancerSentinelAnalytics.json) | [`prancer_CL`](../tables/prancer-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                           |
|-------------|--------------------------------|----------------------------------------------|
| 3.0.1       | 19-03-2024                     | Updated **Workbook**, **Analytic Rules** and **Hunting Queries**                    |
| 3.0.0       | 20-09-2023                     | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
