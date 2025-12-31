# Microsoft Purview

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Purview](../connectors/microsoftazurepurview.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md) | [Microsoft Purview](../connectors/microsoftazurepurview.md) | Analytics, Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Sensitive Data Discovered in the Last 24 Hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Analytic%20Rules/MicrosoftPurviewSensitiveDataDiscovered.yaml) | Informational | Discovery | [`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md) |
| [Sensitive Data Discovered in the Last 24 Hours - Customized](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Analytic%20Rules/MicrosoftPurviewSensitiveDataDiscoveredCustom.yaml) | Informational | Discovery | [`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MicrosoftPurview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Purview/Workbooks/MicrosoftPurview.json) | [`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                            |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------------|
| 3.0.0       | 27-03-2025                     |	**Data Connector** [Microsoft Purview] Globally Available |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
