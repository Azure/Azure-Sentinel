# PaloAltoCDL

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md)

**Publisher:** Palo Alto Networks

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_PaloAlto_CDL_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Data%20Connectors/Connector_PaloAlto_CDL_CEF.json) |

[→ View full connector details](../connectors/paloaltocdl.md)

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md)

**Publisher:** Palo Alto Networks

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PaloAlto_CDLAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Data%20Connectors/template_PaloAlto_CDLAMA.json) |

[→ View full connector details](../connectors/paloaltocdlama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md), [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 12-11-2024                     | Removed Deprecated **Data Connector**                              |
| 3.0.2       | 12-07-2024                     | Deprecated **Data Connector**                                      |
| 3.0.1       | 12-06-2024                     | Optimized parser                                                   |
| 3.0.0       | 25-09-2023                     | Addition of new PaloAltoCDL AMA **Data Connector**                 |

[← Back to Solutions Index](../solutions-index.md)
