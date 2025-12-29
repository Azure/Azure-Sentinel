# Claroty

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Claroty via Legacy Agent](../connectors/claroty.md)

**Publisher:** Claroty

The [Claroty](https://claroty.com/) data connector provides the capability to ingest [Continuous Threat Detection](https://claroty.com/resources/datasheets/continuous-threat-detection) and [Secure Remote Access](https://claroty.com/industrial-cybersecurity/sra) events into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_Claroty_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Data%20Connectors/Connector_Claroty_CEF.json) |

[→ View full connector details](../connectors/claroty.md)

### [[Deprecated] Claroty via AMA](../connectors/clarotyama.md)

**Publisher:** Claroty

The [Claroty](https://claroty.com/) data connector provides the capability to ingest [Continuous Threat Detection](https://claroty.com/resources/datasheets/continuous-threat-detection) and [Secure Remote Access](https://claroty.com/industrial-cybersecurity/sra) events into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ClarotyAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Claroty/Data%20Connectors/template_ClarotyAMA.json) |

[→ View full connector details](../connectors/clarotyama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Claroty via AMA](../connectors/clarotyama.md), [[Deprecated] Claroty via Legacy Agent](../connectors/claroty.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.3       | 18-11-2024                     | Removed Deprecated **Data Connectors**         |  
| 3.0.2 	  | 10-07-2024 					   | Deprecated **Data Connector** 					|
| 3.0.1       | 11-09-2023                     | Addition of new Claroty AMA **Data Connector** |
| 3.0.0       | 27-07-2023                     | Corrected the links in the solution.           |

[← Back to Solutions Index](../solutions-index.md)
