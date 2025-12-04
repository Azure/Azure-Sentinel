# VirtualMetric DataStream

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | VirtualMetric |
| **Support Tier** | Partner |
| **Support Link** | [https://support.virtualmetric.com](https://support.virtualmetric.com) |
| **Categories** | domains |
| **Author** | VirtualMetric |
| **First Published** | 2025-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md)

**Publisher:** VirtualMetric

### [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md)

**Publisher:** VirtualMetric

### [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md)

**Publisher:** VirtualMetric

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel data lake.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Template_SentinelDataLake.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-SentinelDataLake/Template_SentinelDataLake.json) |

[→ View full connector details](../connectors/virtualmetricmssentineldatalakeconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md), [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md), [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md) |

[← Back to Solutions Index](../solutions-index.md)
