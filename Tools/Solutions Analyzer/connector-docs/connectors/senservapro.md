# SenservaPro (Preview)

| | |
|----------|-------|
| **Connector ID** | `SenservaPro` |
| **Publisher** | Senserva |
| **Tables Ingested** | [`SenservaPro_CL`](../tables-index.md#senservapro_cl) |
| **Used in Solutions** | [SenservaPro](../solutions/senservapro.md) |
| **Connector Definition Files** | [SenservaPro.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Data%20Connectors/SenservaPro.json) |

The SenservaPro data connector provides a viewing experience for your SenservaPro scanning logs. View dashboards of your data, use queries to hunt & explore, and create custom alerts.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Setup the data connection**

Visit [Senserva Setup](https://www.senserva.com/senserva-microsoft-sentinel-edition-setup/) for information on setting up the Senserva data connection, support, or any other questions. The Senserva installation will configure a Log Analytics Workspace for output. Deploy Microsoft Sentinel onto the configured Log Analytics Workspace to finish the data connection setup by following [this onboarding guide.](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
