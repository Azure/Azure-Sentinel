# IONIX

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | IONIX |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ionix.io/contact-us/](https://www.ionix.io/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md)

**Publisher:** IONIX

The IONIX Security Logs data connector, ingests logs from the IONIX system directly into Sentinel. The connector allows users to visualize their data, create alerts and incidents and improve security investigations.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **IONIX Subscription**: a subscription and account is required for IONIX logs. [One can be acquired here.](https://azuremarketplace.microsoft.com/en/marketplace/apps/cyberpion1597832716616.cyberpion)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow the [instructions](https://www.ionix.io/integrations/azure-sentinel/) to integrate IONIX Security Alerts into Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `CyberpionActionItems_CL` |
| **Connector Definition Files** | [IONIXSecurityLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IONIX/Data%20Connectors/IONIXSecurityLogs.json) |

[→ View full connector details](../connectors/cyberpionsecuritylogs.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyberpionActionItems_CL` | [IONIX Security Logs](../connectors/cyberpionsecuritylogs.md) |

[← Back to Solutions Index](../solutions-index.md)
