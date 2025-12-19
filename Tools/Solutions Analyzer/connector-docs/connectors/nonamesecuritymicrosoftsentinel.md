# Noname Security for Microsoft Sentinel

| | |
|----------|-------|
| **Connector ID** | `NonameSecurityMicrosoftSentinel` |
| **Publisher** | Noname Security |
| **Tables Ingested** | [`NonameAPISecurityAlert_CL`](../tables-index.md#nonameapisecurityalert_cl) |
| **Used in Solutions** | [NonameSecurity](../solutions/nonamesecurity.md) |
| **Connector Definition Files** | [Connector_RESTAPI_NonameSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NonameSecurity/Data%20Connectors/Connector_RESTAPI_NonameSecurity.json) |

Noname Security solution to POST data into a Microsoft Sentinel SIEM workspace via the Azure Monitor REST API

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure the Noname Sentinel integration.**

Configure the Sentinel workflow in the Noname integrations settings.  Find documentation at https://docs.nonamesecurity.com
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
