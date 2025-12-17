# Microsoft Entra ID Assets

| | |
|----------|-------|
| **Connector ID** | `EntraIDAssets` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Microsoft Entra ID Assets](../solutions/microsoft-entra-id-assets.md) |
| **Connector Definition Files** | [EntraIDAssets_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Assets/Data%20Connectors/EntraIDAssets_DataConnectorDefinition.json) |

Entra ID assets data connector gives richer insights into activity data by supplementing details with asset information. Data from this connector is used to build data risk graphs in Purview. If you have enabled those graphs, deactivating this Connector will prevent the graphs from being built. [Learn about the data risk graph.](https://go.microsoft.com/fwlink/?linkid=2320023)

## Permissions

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1. Connect Microsoft Entra ID assets to ingest into Microsoft Sentinel Lake.
  - Applications
  - Group Memberships
  - Groups
  - Members
  - Organizations
  - Service Principals
  - Users

[← Back to Connectors Index](../connectors-index.md)
