# AtlassianConfluenceAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Atlassian Confluence](../connectors/atlassianconfluence.md)

**Publisher:** Atlassian

The Atlassian Confluence data connector provides the capability to ingest [Atlassian Confluence audit logs](https://developer.atlassian.com/cloud/confluence/rest/api-group-audit/) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `AtlassianConfluenceNativePoller_CL` |
| **Connector Definition Files** | [azuredeploy_Confluence_native_poller_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/ConfluenceNativePollerConnector/azuredeploy_Confluence_native_poller_connector.json) |

[→ View full connector details](../connectors/atlassianconfluence.md)

### [[Deprecated] Atlassian Confluence Audit](../connectors/confluenceauditapi.md)

**Publisher:** Atlassian

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Confluence_Audit_CL` |
| **Connector Definition Files** | [ConfluenceAudit_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditDataConnector/ConfluenceAudit_API_FunctionApp.json) |

[→ View full connector details](../connectors/confluenceauditapi.md)

### [ Atlassian Confluence Audit (via Codeless Connector Framework)](../connectors/confluenceauditccpdefinition.md)

**Publisher:** Microsoft

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ConfluenceAuditLogs_CL` |
| **Connector Definition Files** | [AtlassianConfluenceAudit_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Data%20Connectors/AtlassianConfluenceAuditLogs_CCP/AtlassianConfluenceAudit_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/confluenceauditccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AtlassianConfluenceNativePoller_CL` | [Atlassian Confluence](../connectors/atlassianconfluence.md) |
| `ConfluenceAuditLogs_CL` | [ Atlassian Confluence Audit (via Codeless Connector Framework)](../connectors/confluenceauditccpdefinition.md) |
| `Confluence_Audit_CL` | [[Deprecated] Atlassian Confluence Audit](../connectors/confluenceauditapi.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                    |
|-------------|--------------------------------|-------------------------------------------------------|
| 3.0.6       | 28-07-2025                     | Removed Deprecated **Data Connector**.  |
| 3.0.5       | 06-05-2025                     | Launching CCP **Data Connector** - *Atlassian Confluence Audit* from Public Preview to Global Availability.           |
| 3.0.4       | 16-04-2025                     | Updated **Parser** to support new and old table. <br/>Updated table name in **CCP Connector**.           |
| 3.0.3       | 21-02-2025                     | Added new CCP **Data Connector** 'Atlassian Confluence Audit'.<br/>Added new **Parser** 'ConfluenceAuditV2'.           |
| 3.0.2       | 09-09-2024                     | Updated the Python runtime version to 3.11 in **Data Connector** Function APP.            |
| 3.0.1       | 03-05-2024                     | Repackaged for **Parser** issue fix on reinstall.   	   |
| 3.0.0       | 19-07-2023                     | Updated to enable solution for **Azure government**.  |

[← Back to Solutions Index](../solutions-index.md)
