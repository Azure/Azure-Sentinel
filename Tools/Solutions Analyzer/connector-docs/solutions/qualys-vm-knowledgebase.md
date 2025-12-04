# Qualys VM Knowledgebase

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Qualys VM KnowledgeBase](../connectors/qualyskb.md)

**Publisher:** Qualys

The [Qualys Vulnerability Management (VM)](https://www.qualys.com/apps/vulnerability-management/) KnowledgeBase (KB) connector provides the capability to ingest the latest vulnerability data from the Qualys KB into Microsoft Sentinel. 



 This data can used to correlate and enrich vulnerability detections found by the [Qualys Vulnerability Management (VM)](https://docs.microsoft.com/azure/sentinel/connect-qualys-vm) data connector.

| | |
|--------------------------|---|
| **Tables Ingested** | `QualysKB_CL` |
| **Connector Definition Files** | [QualysKB_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Qualys%20VM%20Knowledgebase/Data%20Connectors/QualysKB_API_FunctionApp.json) |

[→ View full connector details](../connectors/qualyskb.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `QualysKB_CL` | [Qualys VM KnowledgeBase](../connectors/qualyskb.md) |

[← Back to Solutions Index](../solutions-index.md)
