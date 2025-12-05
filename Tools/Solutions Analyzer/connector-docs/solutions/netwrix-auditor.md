# Netwrix Auditor

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Netwrix Auditor via Legacy Agent](../connectors/netwrix.md)

**Publisher:** Netwrix

### [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md)

**Publisher:** Netwrix

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_NetwrixAuditorAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/template_NetwrixAuditorAMA.json) |

[→ View full connector details](../connectors/netwrixama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md), [[Deprecated] Netwrix Auditor via Legacy Agent](../connectors/netwrix.md) |

[← Back to Solutions Index](../solutions-index.md)
