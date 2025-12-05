# Microsoft Defender for Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md)

**Publisher:** Microsoft

Microsoft Defender for Cloud is a security management tool that allows you to detect and quickly respond to threats across Azure, hybrid, and multi-cloud workloads. This connector allows you to stream your MDC security alerts from Microsoft 365 Defender into Microsoft Sentinel, so you can can leverage the advantages of XDR correlations connecting the dots across your cloud resources, devices and identities and view the data in workbooks, queries and investigate and respond to incidents. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269832&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [MicrosoftDefenderForCloudTenantBased.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Data%20Connectors/MicrosoftDefenderForCloudTenantBased.json) |

[→ View full connector details](../connectors/microsoftdefenderforcloudtenantbased.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Tenant-based Microsoft Defender for Cloud](../connectors/microsoftdefenderforcloudtenantbased.md) |

[← Back to Solutions Index](../solutions-index.md)
