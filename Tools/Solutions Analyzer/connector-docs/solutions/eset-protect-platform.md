# ESET Protect Platform

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ESET Enterprise Integrations |
| **Support Tier** | Partner |
| **Support Link** | [https://help.eset.com/eset_connect/en-US/integrations.html](https://help.eset.com/eset_connect/en-US/integrations.html) |
| **Categories** | domains |
| **First Published** | 2024-10-29 |
| **Last Updated** | 2025-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ESET Protect Platform](../connectors/esetprotectplatform.md)

**Publisher:** ESET

The ESET Protect Platform data connector enables users to inject detections data from [ESET Protect Platform](https://www.eset.com/int/business/protect-platform/) using the provided [Integration REST API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Data%20Connectors). Integration REST API runs as scheduled Azure Function App.

| | |
|--------------------------|---|
| **Tables Ingested** | `IntegrationTableIncidents_CL` |
| | `IntegrationTable_CL` |
| **Connector Definition Files** | [ESETProtectPlatform_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Data%20Connectors/ESETProtectPlatform_API_FunctionApp.json) |

[→ View full connector details](../connectors/esetprotectplatform.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `IntegrationTableIncidents_CL` | [ESET Protect Platform](../connectors/esetprotectplatform.md) |
| `IntegrationTable_CL` | [ESET Protect Platform](../connectors/esetprotectplatform.md) |

[← Back to Solutions Index](../solutions-index.md)
