# CiscoSEG

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](../connectors/ciscoseg.md)

**Publisher:** Cisco

The [Cisco Secure Email Gateway (SEG)](https://www.cisco.com/c/en/us/products/security/email-security/index.html) data connector provides the capability to ingest [Cisco SEG Consolidated Event Logs](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1061902) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_Cisco_SEG_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Data%20Connectors/Connector_Cisco_SEG_CEF.json) |

[→ View full connector details](../connectors/ciscoseg.md)

### [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md)

**Publisher:** Cisco

The [Cisco Secure Email Gateway (SEG)](https://www.cisco.com/c/en/us/products/security/email-security/index.html) data connector provides the capability to ingest [Cisco SEG Consolidated Event Logs](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1061902) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CiscoSEGAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Data%20Connectors/template_CiscoSEGAMA.json) |

[→ View full connector details](../connectors/ciscosegama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md), [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](../connectors/ciscoseg.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.5       | 02-12-2024                     | Added Missed Column **Parser**                                     |
| 3.0.4       | 14-11-2024                     | Removed Deprecated **Data Connector**                              |
| 3.0.3       | 08-07-2024                     | Deprecated **Data Connector**   								    |
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall                       |
| 3.0.1       | 30-04-2024                     | Updated the **Data Connector** to fix conectivity criteria query   |
| 3.0.0       | 28-09-2023                     | Addition of new CiscoSEG AMA **Data Connector**                 | 	                                                            |

[← Back to Solutions Index](../solutions-index.md)
