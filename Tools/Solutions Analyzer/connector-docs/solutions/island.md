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
