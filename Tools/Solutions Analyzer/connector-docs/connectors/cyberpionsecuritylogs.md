# IONIX Security Logs

| | |
|----------|-------|
| **Connector ID** | `CyberpionSecurityLogs` |
| **Publisher** | IONIX |
| **Tables Ingested** | [`CyberpionActionItems_CL`](../tables-index.md#cyberpionactionitems_cl) |
| **Used in Solutions** | [IONIX](../solutions/ionix.md) |
| **Connector Definition Files** | [IONIXSecurityLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX/Data%20Connectors/IONIXSecurityLogs.json) |

The IONIX Security Logs data connector, ingests logs from the IONIX system directly into Sentinel. The connector allows users to visualize their data, create alerts and incidents and improve security investigations.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **IONIX Subscription**: a subscription and account is required for IONIX logs. [One can be acquired here.](https://azuremarketplace.microsoft.com/en/marketplace/apps/cyberpion1597832716616.cyberpion)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the [instructions](https://www.ionix.io/integrations/azure-sentinel/) to integrate IONIX Security Alerts into Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
