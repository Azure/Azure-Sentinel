# PaloAltoCDL

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md)

**Publisher:** Palo Alto Networks

The [Palo Alto Networks CDL](https://www.paloaltonetworks.com/cortex/cortex-data-lake) data connector provides the capability to ingest [CDL logs](https://docs.paloaltonetworks.com/strata-logging-service/log-reference/log-forwarding-schema-overview) into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PaloAlto_CDLAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PaloAltoCDL/Data%20Connectors/template_PaloAlto_CDLAMA.json) |

[→ View full connector details](../connectors/paloaltocdlama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via AMA](../connectors/paloaltocdlama.md), [[Deprecated] Palo Alto Networks Cortex Data Lake (CDL) via Legacy Agent](../connectors/paloaltocdl.md) |

[← Back to Solutions Index](../solutions-index.md)
