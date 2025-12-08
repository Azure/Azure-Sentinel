# Red Canary

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Red Canary |
| **Support Tier** | Partner |
| **Support Link** | [https://www.redcanary.com](https://www.redcanary.com) |
| **Categories** | domains |
| **First Published** | 2022-03-04 |
| **Last Updated** | 2022-03-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Red Canary Threat Detection](../connectors/redcanarydataconnector.md)

**Publisher:** Red Canary

The Red Canary data connector provides the capability to ingest published Detections into Microsoft Sentinel using the Data Collector REST API.

| | |
|--------------------------|---|
| **Tables Ingested** | `RedCanaryDetections_CL` |
| **Connector Definition Files** | [RedCanaryDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Red%20Canary/Data%20Connectors/RedCanaryDataConnector.json) |

[→ View full connector details](../connectors/redcanarydataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `RedCanaryDetections_CL` | [Red Canary Threat Detection](../connectors/redcanarydataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
