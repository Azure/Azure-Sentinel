# Microsoft Defender for Cloud Apps

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`McasShadowItReporting`](../tables/mcasshadowitreporting.md) | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) | Workbooks |
| [`StorageBlobLogs`](../tables/storagebloblogs.md) | - | Analytics |
| [`discoveryLogs`](../tables/discoverylogs.md) | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) | - |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Defender for Cloud Apps](../connectors/microsoftcloudappsecurity.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Linked Malicious Storage Artifacts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps/Analytic%20Rules/AdditionalFilesUploadedByActor.yaml) | Medium | CommandAndControl, Exfiltration | [`StorageBlobLogs`](../tables/storagebloblogs.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MicrosoftCloudAppSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud%20Apps/Workbooks/MicrosoftCloudAppSecurity.json) | [`McasShadowItReporting`](../tables/mcasshadowitreporting.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.0       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
