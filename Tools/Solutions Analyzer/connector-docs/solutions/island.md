# Island

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Island |
| **Support Tier** | Partner |
| **Support Link** | [https://www.island.io](https://www.island.io) |
| **Categories** | domains |
| **First Published** | 2023-05-02 |
| **Last Updated** | 2023-07-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Island Enterprise Browser Admin Audit (Polling CCP)](../connectors/island-admin-polling.md)

**Publisher:** Island

### [Island Enterprise Browser User Activity (Polling CCP)](../connectors/island-user-polling.md)

**Publisher:** Island

The [Island](https://www.island.io) connector provides the capability to ingest Island User Activity logs into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Island API Key**: An Island API key is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Island to Microsoft Sentinel**

Provide the Island API URL and Key.  API URL is https://management.island.io/api/external/v1/timeline for US or https://eu.management.island.io/api/external/v1/timeline for EU.
  Generate the API Key in the Management Console under Settings > API.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `Island_User_CL` |
| **Connector Definition Files** | [IslandUserAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Island/Data%20Connectors/IslandUserAPIConnector.json) |

[→ View full connector details](../connectors/island-user-polling.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Island_Admin_CL` | [Island Enterprise Browser Admin Audit (Polling CCP)](../connectors/island-admin-polling.md) |
| `Island_User_CL` | [Island Enterprise Browser User Activity (Polling CCP)](../connectors/island-user-polling.md) |

[← Back to Solutions Index](../solutions-index.md)
