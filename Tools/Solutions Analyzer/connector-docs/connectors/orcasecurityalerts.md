# Orca Security Alerts

| | |
|----------|-------|
| **Connector ID** | `OrcaSecurityAlerts` |
| **Publisher** | Orca Security |
| **Tables Ingested** | [`OrcaAlerts_CL`](../tables-index.md#orcaalerts_cl) |
| **Used in Solutions** | [Orca Security Alerts](../solutions/orca-security-alerts.md) |
| **Connector Definition Files** | [OrcaSecurityAlerts.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Orca%20Security%20Alerts/Data%20Connectors/OrcaSecurityAlerts.json) |

The Orca Security Alerts connector allows you to easily export Alerts logs to Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow [guidance](https://orcasecurity.zendesk.com/hc/en-us/articles/360043941992-Azure-Sentinel-configuration) for integrating Orca Security Alerts logs with Microsoft Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
