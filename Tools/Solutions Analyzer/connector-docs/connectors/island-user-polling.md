# Island Enterprise Browser User Activity (Polling CCP)

| | |
|----------|-------|
| **Connector ID** | `Island_User_Polling` |
| **Publisher** | Island |
| **Tables Ingested** | [`Island_User_CL`](../tables-index.md#island_user_cl) |
| **Used in Solutions** | [Island](../solutions/island.md) |
| **Connector Definition Files** | [IslandUserAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island/Data%20Connectors/IslandUserAPIConnector.json) |

The [Island](https://www.island.io) connector provides the capability to ingest Island User Activity logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Island API Key**: An Island API key is required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Island to Microsoft Sentinel**

Provide the Island API URL and Key.  API URL is https://management.island.io/api/external/v1/timeline for US or https://eu.management.island.io/api/external/v1/timeline for EU.
  Generate the API Key in the Management Console under Settings > API.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
