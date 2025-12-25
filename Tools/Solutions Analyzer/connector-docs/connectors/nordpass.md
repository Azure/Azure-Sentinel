# NordPass

| | |
|----------|-------|
| **Connector ID** | `NordPass` |
| **Publisher** | NordPass |
| **Tables Ingested** | [`NordPassEventLogs_CL`](../tables-index.md#nordpasseventlogs_cl) |
| **Used in Solutions** | [NordPass](../solutions/nordpass.md) |
| **Connector Definition Files** | [NordPass_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Data%20Connectors/NordPass_API_FunctionApp.json), [NordPass_data_connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NordPass/Data%20Connectors/deployment/NordPass_data_connector.json) |

Integrating NordPass with Microsoft Sentinel SIEM via the API will allow you to automatically transfer Activity Log data from NordPass to Microsoft Sentinel and get real-time insights, such as item activity, all login attempts, and security notifications.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

To proceed with the Microsoft Sentinel setup

1. Click the **Deploy to Azure** button below. 

	[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/sentinel-Nordpass-azuredeploy)
2. **Please note that after the successful deployment, the system pulls Activity Log data every 1 minute by default.**

[← Back to Connectors Index](../connectors-index.md)
