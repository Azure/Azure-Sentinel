# ExtraHop

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ExtraHop Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.extrahop.com/customer-support](https://www.extrahop.com/customer-support) |
| **Categories** | domains |
| **First Published** | 2025-02-11 |
| **Last Updated** | 2025-06-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ExtraHop Detections Data Connector](../connectors/extrahop.md)

**Publisher:** ExtraHop

The [ExtraHop](https://extrahop.com/) Detections Data Connector enables you to import detection data from ExtraHop RevealX to Microsoft Sentinel through webhook payloads.

| | |
|--------------------------|---|
| **Tables Ingested** | `ExtraHop_Detections_CL` |
| **Connector Definition Files** | [ExtraHop_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ExtraHop/Data%20Connectors/ExtraHopDataConnector/ExtraHop_FunctionApp.json) |

[→ View full connector details](../connectors/extrahop.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ExtraHop_Detections_CL` | [ExtraHop Detections Data Connector](../connectors/extrahop.md) |

[← Back to Solutions Index](../solutions-index.md)
