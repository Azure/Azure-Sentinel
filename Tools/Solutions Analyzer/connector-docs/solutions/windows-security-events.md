# Windows Security Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Security Events via Legacy Agent](../connectors/securityevents.md)

**Publisher:** Microsoft

You can stream all security events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220093&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityEvent` |
| **Connector Definition Files** | [template_SecurityEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Data%20Connectors/template_SecurityEvents.JSON) |

[→ View full connector details](../connectors/securityevents.md)

### [Windows Security Events via AMA](../connectors/windowssecurityevents.md)

**Publisher:** Microsoft

You can stream all security events from the Windows machines connected to your Microsoft Sentinel workspace using the Windows agent. This connection enables you to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization’s network and improves your security operation capabilities. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2220225&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityEvent` |
| **Connector Definition Files** | [template_WindowsSecurityEvents.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Windows%20Security%20Events/Data%20Connectors/template_WindowsSecurityEvents.JSON) |

[→ View full connector details](../connectors/windowssecurityevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityEvent` | [Security Events via Legacy Agent](../connectors/securityevents.md), [Windows Security Events via AMA](../connectors/windowssecurityevents.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                         |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------|
| 3.0.9       | 01-10-2024                     | Removed kind from  **Hunting Query** [Service installation from user writable directory]   |
| 3.0.8       | 23-07-2024                     | Updated the Workspace type from resource type picker to resource picker in **Workbook**    |
| 3.0.7       | 12-06-2024                     | Fixed the bugs from **Analytic Rules** NRT_execute_base64_decodedpayload.yaml and ADFSRemoteAuthSyncConnection.yaml |												
| 3.0.6       | 16-05-2024                     | Fixed wrong fieldMappings of **Analytic Rules** password_not_set.yaml						|												
| 3.0.5       | 21-03-2024                     | Updated Entity Mappings of **Analytic Rules** 												|					|
| 3.0.4       | 06-03-2024                     | Added New **Hunting Queries**																	|
| 3.0.3       | 19-02-2024                     | Updated Entity Mapping in 	**Analytical Rule** [Non Domain Controller Active Directory Replication]														|
| 3.0.2       | 23-01-2024                     | Added Sub-Technique in Template															|
| 3.0.1       | 13-12-2023                     | Updated query in **Analytical Rule** (AD user enabled and password not set within 48 hours)|
| 3.0.0       | 26-12-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.                   |

[← Back to Solutions Index](../solutions-index.md)
