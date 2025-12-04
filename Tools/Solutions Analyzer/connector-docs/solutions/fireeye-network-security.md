# FireEye Network Security

## Solution Information

| | |
|------------------------|-------|
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

### [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md)

**Publisher:** FireEye

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_FireEyeNX_CEFAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/template_FireEyeNX_CEFAMA.json) |

[→ View full connector details](../connectors/fireeyenxama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] FireEye Network Security (NX) via AMA](../connectors/fireeyenxama.md), [[Deprecated] FireEye Network Security (NX) via Legacy Agent](../connectors/fireeyenx.md) |

[← Back to Solutions Index](../solutions-index.md)
