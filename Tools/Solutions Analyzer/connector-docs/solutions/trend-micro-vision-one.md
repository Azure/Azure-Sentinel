# Trend Micro Vision One

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/?language=en_US](https://success.trendmicro.com/dcx/s/?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Last Updated** | 2024-07-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Trend Vision One](../connectors/trendmicroxdr.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`TrendMicro_XDR_OAT_CL`](../tables/trendmicro-xdr-oat-cl.md) | [Trend Vision One](../connectors/trendmicroxdr.md) | - |
| [`TrendMicro_XDR_RCA_Result_CL`](../tables/trendmicro-xdr-rca-result-cl.md) | [Trend Vision One](../connectors/trendmicroxdr.md) | - |
| [`TrendMicro_XDR_RCA_Task_CL`](../tables/trendmicro-xdr-rca-task-cl.md) | [Trend Vision One](../connectors/trendmicroxdr.md) | - |
| [`TrendMicro_XDR_WORKBENCH_CL`](../tables/trendmicro-xdr-workbench-cl.md) | [Trend Vision One](../connectors/trendmicroxdr.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Create Incident for XDR Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One/Analytic%20Rules/Create%20Incident%20for%20XDR%20Alerts.yaml) | High | - | [`TrendMicro_XDR_WORKBENCH_CL`](../tables/trendmicro-xdr-workbench-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TrendMicroXDROverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Vision%20One/Workbooks/TrendMicroXDROverview.json) | [`TrendMicro_XDR_WORKBENCH_CL`](../tables/trendmicro-xdr-workbench-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 30-01-2025                     | Updated hyperlink in **Data Connector**     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
