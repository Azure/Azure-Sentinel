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

This solution provides **3 data connector(s)**:

- [Atlassian Confluence](../connectors/atlassianconfluence.md)
- [[Deprecated] Atlassian Confluence Audit](../connectors/confluenceauditapi.md)
- [ Atlassian Confluence Audit (via Codeless Connector Framework)](../connectors/confluenceauditccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AtlassianConfluenceNativePoller_CL`](../tables/atlassianconfluencenativepoller-cl.md) | [Atlassian Confluence](../connectors/atlassianconfluence.md) | - |
| [`ConfluenceAuditLogs_CL`](../tables/confluenceauditlogs-cl.md) | [ Atlassian Confluence Audit (via Codeless Connector Framework)](../connectors/confluenceauditccpdefinition.md) | - |
| [`Confluence_Audit_CL`](../tables/confluence-audit-cl.md) | [[Deprecated] Atlassian Confluence Audit](../connectors/confluenceauditapi.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ConfluenceAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AtlassianConfluenceAudit/Parsers/ConfluenceAudit.yaml) | - | - |

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

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
