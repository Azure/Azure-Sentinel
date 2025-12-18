# SenservaPro

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Senserva |
| **Support Tier** | Partner |
| **Support Link** | [https://www.senserva.com/contact/](https://www.senserva.com/contact/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SenservaPro (Preview)](../connectors/senservapro.md)

**Publisher:** Senserva

The SenservaPro data connector provides a viewing experience for your SenservaPro scanning logs. View dashboards of your data, use queries to hunt & explore, and create custom alerts.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Setup the data connection**

Visit [Senserva Setup](https://www.senserva.com/senserva-microsoft-sentinel-edition-setup/) for information on setting up the Senserva data connection, support, or any other questions. The Senserva installation will configure a Log Analytics Workspace for output. Deploy Microsoft Sentinel onto the configured Log Analytics Workspace to finish the data connection setup by following [this onboarding guide.](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `SenservaPro_CL` |
| **Connector Definition Files** | [SenservaPro.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Data%20Connectors/SenservaPro.json) |

[→ View full connector details](../connectors/senservapro.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SenservaPro_CL` | [SenservaPro (Preview)](../connectors/senservapro.md) |

[← Back to Solutions Index](../solutions-index.md)
