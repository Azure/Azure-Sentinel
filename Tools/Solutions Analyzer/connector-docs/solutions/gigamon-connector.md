# Gigamon Connector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Gigamon |
| **Support Tier** | Partner |
| **Support Link** | [https://www.gigamon.com/](https://www.gigamon.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md)

**Publisher:** Gigamon

Use this data connector to integrate with Gigamon Application Metadata Exporter (AMX) and get data sent directly to Microsoft Sentinel. 

| | |
|--------------------------|---|
| **Tables Ingested** | `Gigamon_CL` |
| **Connector Definition Files** | [Connector_Analytics_Gigamon.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Gigamon%20Connector/Data%20Connectors/Connector_Analytics_Gigamon.json) |

[→ View full connector details](../connectors/gigamondataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Gigamon_CL` | [Gigamon AMX Data Connector](../connectors/gigamondataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
