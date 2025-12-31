# Microsoft Defender for Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md)
- [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CoreAzureBackup`](../tables/coreazurebackup.md) | - | Analytics |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md), [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md) | Analytics |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Detect CoreBackUp Deletion Activity from related Security Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Analytic%20Rules/CoreBackupDeletionwithSecurityAlert.yaml) | Medium | Impact | [`CoreAzureBackup`](../tables/coreazurebackup.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                              |
|-------------|-------------------------------|-------------------------------------------------|
| 3.0.3       |	06-12-2025	                  |Moved MicrosoftDefenderForCloudTenantBased's **Data Connector** from public preview to Global Availability | 
| 3.0.2       |	15-04-2024	                  |Updated **Data Connector** MicrosoftDefenderForCloudTenantBased's kind as GenericUI | 
| 3.0.1       | 03-04-2024                    |Corrected the standard tier in **Data Connector** and Updated MicrosoftDefenderForCloudTenantBased.json to support FFX  |
| 3.0.0       | 08-11-2023                    |New **Data Connector** included		        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
