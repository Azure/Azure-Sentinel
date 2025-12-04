# ESET Inspect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ESET Enterprise |
| **Support Tier** | Partner |
| **Support Link** | [https://www.eset.com/int/business/solutions/endpoint-detection-and-response/](https://www.eset.com/int/business/solutions/endpoint-detection-and-response/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ESET Inspect](../connectors/esetinspect.md)

**Publisher:** ESET Netherlands

This connector will ingest detections from [ESET Inspect](https://www.eset.com/int/business/solutions/xdr-extended-detection-and-response/) using the provided [REST API](https://help.eset.com/ei_navigate/latest/en-US/api.html). This API is present in ESET Inspect version 1.4 and later.

| | |
|--------------------------|---|
| **Tables Ingested** | `ESETInspect_CL` |
| **Connector Definition Files** | [ESETInspect_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Inspect/Data%20Connectors/ESETInspect_API_FunctionApp.json) |

[→ View full connector details](../connectors/esetinspect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ESETInspect_CL` | [ESET Inspect](../connectors/esetinspect.md) |

[← Back to Solutions Index](../solutions-index.md)
