# FireEye Network Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] FireEye Network Security (NX) via Legacy Agent](../connectors/fireeyenx.md)

**Publisher:** FireEye

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_FireEyeNX_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/Connector_FireEyeNX_CEF.json) |

[→ View full connector details](../connectors/fireeyenx.md)

### [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md)

**Publisher:** FireEye

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_FireEyeNX_CEFAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/template_FireEyeNX_CEFAMA.json) |

[→ View full connector details](../connectors/fireeyenxama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md), [[Deprecated] FireEye Network Security (NX) via Legacy Agent](../connectors/fireeyenx.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 21-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 10-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 01-09-2023                     |	Addition of new FireEye Network Security AMA **Data Connector** |

[← Back to Solutions Index](../solutions-index.md)
