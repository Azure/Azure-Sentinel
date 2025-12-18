# Orca Security Alerts

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Orca Security |
| **Support Tier** | Partner |
| **Support Link** | [https://orca.security/about/contact/](https://orca.security/about/contact/) |
| **Categories** | domains |
| **First Published** | 2022-05-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Orca%20Security%20Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Orca%20Security%20Alerts) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Orca Security Alerts](../connectors/orcasecurityalerts.md)

**Publisher:** Orca Security

The Orca Security Alerts connector allows you to easily export Alerts logs to Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Follow [guidance](https://orcasecurity.zendesk.com/hc/en-us/articles/360043941992-Azure-Sentinel-configuration) for integrating Orca Security Alerts logs with Microsoft Sentinel.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `OrcaAlerts_CL` |
| **Connector Definition Files** | [OrcaSecurityAlerts.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Orca%20Security%20Alerts/Data%20Connectors/OrcaSecurityAlerts.json) |

[→ View full connector details](../connectors/orcasecurityalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `OrcaAlerts_CL` | [Orca Security Alerts](../connectors/orcasecurityalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
