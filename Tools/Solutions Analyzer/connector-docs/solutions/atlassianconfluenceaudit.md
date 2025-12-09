# AtlassianConfluenceAudit

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Atlassian Confluence Audit](../connectors/confluenceauditapi.md)

**Publisher:** Atlassian

### [ Atlassian Confluence Audit (via Codeless Connector Framework)](../connectors/confluenceauditccpdefinition.md)

**Publisher:** Microsoft

The [Atlassian Confluence](https://www.atlassian.com/software/confluence) Audit data connector provides the capability to ingest [Confluence Audit Records](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) events into Microsoft Sentinel through the REST API. Refer to [API documentation](https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/) for more information. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
