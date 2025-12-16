# Lookout Mobile Threat Detection Connector (via Codeless Connector Framework) (Preview)

| | |
|----------|-------|
| **Connector ID** | `LookoutStreaming_Definition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`LookoutMtdV2_CL`](../tables-index.md#lookoutmtdv2_cl) |
| **Used in Solutions** | [Lookout](../solutions/lookout.md) |
| **Connector Definition Files** | [LookoutStreaming_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lookout/Data%20Connectors/LookoutStreamingConnector_ccp/LookoutStreaming_DataConnectorDefinition.json) |

The [Lookout Mobile Threat Detection](https://lookout.com) data connector provides the capability to ingest events related to mobile security risks into Microsoft Sentinel through the Mobile Risk API. Refer to [API documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) for more information. This connector helps you examine potential security risks detected in mobile devices.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions on the workspace are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Lookout Mobile Threat Defence connector to Microsoft Sentinel**
Before connecting to Lookout, ensure the following prerequisites are completed.
#### 1.  **ApiKey** is required for Mobile Threat Detection API. See the [documentation](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide) to learn more about API. Check all requirements and follow  the [instructions](https://enterprise.support.lookout.com/hc/en-us/articles/115002741773-Mobile-Risk-API-Guide#authenticatingwiththemobileriskapi) for obtaining credentials.
- **API key**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
