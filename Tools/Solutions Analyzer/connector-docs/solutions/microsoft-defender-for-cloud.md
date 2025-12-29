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

This solution provides **2 data connector(s)**.

### [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md)

**Publisher:** Microsoft

Microsoft Defender for Cloud is a security management tool that allows you to detect and quickly respond to threats across Azure, hybrid, and multi-cloud workloads. This connector allows you to stream your security alerts from Microsoft Defender for Cloud into Microsoft Sentinel, so you can view Defender data in workbooks, query it to produce alerts, and investigate and respond to incidents.



[For more information>](https://aka.ms/ASC-Connector)

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [AzureSecurityCenter.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Data%20Connectors/AzureSecurityCenter.JSON) |

[→ View full connector details](../connectors/azuresecuritycenter.md)

### [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md)

**Publisher:** Microsoft

Microsoft Defender for Cloud is a security management tool that allows you to detect and quickly respond to threats across Azure, hybrid, and multi-cloud workloads. This connector allows you to stream your MDC security alerts from Microsoft 365 Defender into Microsoft Sentinel, so you can can leverage the advantages of XDR correlations connecting the dots across your cloud resources, devices and identities and view the data in workbooks, queries and investigate and respond to incidents. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269832&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [MicrosoftDefenderForCloudTenantBased.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Data%20Connectors/MicrosoftDefenderForCloudTenantBased.json) |

[→ View full connector details](../connectors/microsoftdefenderforcloudtenantbased.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Subscription-based Microsoft Defender for Cloud (Legacy)](../connectors/azuresecuritycenter.md), [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                              |
|-------------|-------------------------------|-------------------------------------------------|
| 3.0.3       |	06-12-2025	                  |Moved MicrosoftDefenderForCloudTenantBased's **Data Connector** from public preview to Global Availability | 
| 3.0.2       |	15-04-2024	                  |Updated **Data Connector** MicrosoftDefenderForCloudTenantBased's kind as GenericUI | 
| 3.0.1       | 03-04-2024                    |Corrected the standard tier in **Data Connector** and Updated MicrosoftDefenderForCloudTenantBased.json to support FFX  |
| 3.0.0       | 08-11-2023                    |New **Data Connector** included		        |

[← Back to Solutions Index](../solutions-index.md)
