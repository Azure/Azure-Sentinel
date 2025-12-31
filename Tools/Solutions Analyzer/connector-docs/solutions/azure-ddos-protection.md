# Azure DDoS Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure DDoS Protection](../connectors/ddos.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure DDoS Protection](../connectors/ddos.md) | Analytics, Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [DDoS Attack IP Addresses - PPS Threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Analytic%20Rules/AttackSourcesPPSThreshold.yaml) | Medium | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [DDoS Attack IP Addresses - Percent Threshold](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Analytic%20Rules/AttackSourcesPercentThreshold.yaml) | Medium | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AzDDoSStandardWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20DDoS%20Protection/Workbooks/AzDDoSStandardWorkbook.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
