# Microsoft Entra ID Assets

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-06-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Assets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Assets) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Entra ID Assets](../connectors/entraidassets.md)

**Publisher:** Microsoft

Entra ID assets data connector gives richer insights into activity data by supplementing details with asset information. Data from this connector is used to build data risk graphs in Purview. If you have enabled those graphs, deactivating this Connector will prevent the graphs from being built. [Learn about the data risk graph.](https://go.microsoft.com/fwlink/?linkid=2320023)

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `` |
| **Connector Definition Files** | [EntraIDAssets_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Assets/Data%20Connectors/EntraIDAssets_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/entraidassets.md)

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                      |
|-------------|--------------------------------|---------------------------------------------------------------------------------------------------------|
| 3.0.1       | 28-10-2025                     | Fixed a typo in the data connector tile, correcting enta to Entra | 
| 3.0.0       | 11-09-2025                     | Releasing a new Microsoft Entra ID Assets connector solution in Content Hub and Data Connector gallery. |

[← Back to Solutions Index](../solutions-index.md)
