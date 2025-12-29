# CiscoWSA

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md)

**Publisher:** Cisco

[Cisco Web Security Appliance (WSA)](https://www.cisco.com/c/en/us/products/security/web-security-appliance/index.html) data connector provides the capability to ingest [Cisco WSA Access Logs](https://www.cisco.com/c/en/us/td/docs/security/wsa/wsa_14-0/User-Guide/b_WSA_UserGuide_14_0/b_WSA_UserGuide_11_7_chapter_010101.html) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_WSA_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Data%20Connectors/Connector_WSA_Syslog.json) |

[→ View full connector details](../connectors/ciscowsa.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 19-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.1       | 24-07-2024                     | Deprecating data connectors                 |
| 3.0.0       | 16-08-2023                     | Optimize the **Parser** by replacing the legacy code that uses regex with a more efficient algorithm to reduce the time taken to parse data. |

[← Back to Solutions Index](../solutions-index.md)
