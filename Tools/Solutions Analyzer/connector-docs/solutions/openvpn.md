# OpenVPN

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-08-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] OpenVPN Server](../connectors/openvpn.md)

**Publisher:** OpenVPN

The [OpenVPN](https://github.com/OpenVPN) data connector provides the capability to ingest OpenVPN Server logs into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [OpenVPN_Syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenVPN/Data%20Connectors/OpenVPN_Syslog.json) |

[→ View full connector details](../connectors/openvpn.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] OpenVPN Server](../connectors/openvpn.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 18-12-2024                     | Removed Deprecated **Data Connector**       |
| 3.0.0       | 19-07-2024                     | Deprecated **Data Connector**               |

[← Back to Solutions Index](../solutions-index.md)
