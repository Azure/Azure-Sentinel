# VirtualMetric DataStream

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | VirtualMetric |
| **Support Tier** | Partner |
| **Support Link** | [https://support.virtualmetric.com](https://support.virtualmetric.com) |
| **Categories** | domains |
| **Author** | VirtualMetric |
| **First Published** | 2025-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream) |\n\n## Data Connectors

This solution provides **3 data connector(s)**.

### VirtualMetric Director Proxy

**Publisher:** VirtualMetric

VirtualMetric Director Proxy deploys an Azure Function App to securely bridge VirtualMetric DataStream with Azure services including Microsoft Sentinel, Azure Data Explorer, and Azure Storage.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Template_DirectorProxy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-DirectorProxy/Template_DirectorProxy.json)

### VirtualMetric DataStream for Microsoft Sentinel

**Publisher:** VirtualMetric

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Template_Sentinel.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-Sentinel/Template_Sentinel.json)

### VirtualMetric DataStream for Microsoft Sentinel data lake

**Publisher:** VirtualMetric

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel data lake.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Template_SentinelDataLake.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-SentinelDataLake/Template_SentinelDataLake.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 3 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n