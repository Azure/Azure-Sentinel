# Netwrix Auditor

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_NetwrixAuditor.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/Connector_NetwrixAuditor.json) |

[→ View full connector details](../connectors/netwrix.md)

### [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md)

**Publisher:** Netwrix

Netwrix Auditor data connector provides the capability to ingest [Netwrix Auditor (formerly Stealthbits Privileged Activity Manager)](https://www.netwrix.com/auditor.html) events into Microsoft Sentinel. Refer to [Netwrix documentation](https://helpcenter.netwrix.com/) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_NetwrixAuditorAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netwrix%20Auditor/Data%20Connectors/template_NetwrixAuditorAMA.json) |

[→ View full connector details](../connectors/netwrixama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Netwrix Auditor via AMA](../connectors/netwrixama.md), [[Deprecated] Netwrix Auditor via Legacy Agent](../connectors/netwrix.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 22-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 10-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 29-08-2023                     | Addition of new Netwrix Auditor AMA **Data Connector**             |

[← Back to Solutions Index](../solutions-index.md)
