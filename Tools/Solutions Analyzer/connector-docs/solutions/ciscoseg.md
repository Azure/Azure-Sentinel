# CiscoSEG

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md)

**Publisher:** Cisco

The [Cisco Secure Email Gateway (SEG)](https://www.cisco.com/c/en/us/products/security/email-security/index.html) data connector provides the capability to ingest [Cisco SEG Consolidated Event Logs](https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0/b_ESA_Admin_Guide_12_1_chapter_0100111.html#con_1061902) into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CiscoSEGAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoSEG/Data%20Connectors/template_CiscoSEGAMA.json) |

[→ View full connector details](../connectors/ciscosegama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Cisco Secure Email Gateway via AMA](../connectors/ciscosegama.md), [[Deprecated] Cisco Secure Email Gateway via Legacy Agent](../connectors/ciscoseg.md) |

[← Back to Solutions Index](../solutions-index.md)
