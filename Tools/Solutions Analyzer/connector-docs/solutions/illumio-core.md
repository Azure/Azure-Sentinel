# Illumio Core

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Illumio Core via Legacy Agent](../connectors/illumiocore.md)

**Publisher:** Illumio

### [[Deprecated] Illumio Core via AMA](../connectors/illumiocoreama.md)

**Publisher:** Illumio

The [Illumio Core](https://www.illumio.com/products/) data connector provides the capability to ingest Illumio Core logs into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_IllumioCoreAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core/Data%20Connectors/template_IllumioCoreAMA.json) |

[→ View full connector details](../connectors/illumiocoreama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Illumio Core via AMA](../connectors/illumiocoreama.md), [[Deprecated] Illumio Core via Legacy Agent](../connectors/illumiocore.md) |

[← Back to Solutions Index](../solutions-index.md)
