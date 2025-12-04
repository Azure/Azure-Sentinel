# Phosphorus

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Phosphorus Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://phosphorus.io](https://phosphorus.io) |
| **Categories** | domains |
| **First Published** | 2024-08-13 |
| **Last Updated** | 2024-08-13 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Phosphorus Devices](../connectors/phosphorus-polling.md)

**Publisher:** Phosphorus Inc.

The Phosphorus Device Connector provides the capability to Phosphorus to ingest device data logs into Microsoft Sentinel through the Phosphorus REST API. The Connector provides visibility into the devices enrolled in Phosphorus. This Data Connector pulls devices information along with its corresponding alerts.

| | |
|--------------------------|---|
| **Tables Ingested** | `Phosphorus_CL` |
| **Connector Definition Files** | [PhosphorusDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Phosphorus/Data%20Connectors/PhosphorusDataConnector.json) |

[→ View full connector details](../connectors/phosphorus-polling.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Phosphorus_CL` | [Phosphorus Devices](../connectors/phosphorus-polling.md) |

[← Back to Solutions Index](../solutions-index.md)
