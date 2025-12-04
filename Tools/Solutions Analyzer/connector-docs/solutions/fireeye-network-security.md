# FireEye Network Security

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] FireEye Network Security (NX) via Legacy Agent

**Publisher:** FireEye

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Connector_FireEyeNX_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/Connector_FireEyeNX_CEF.json)

### [Deprecated] FireEye Network Security (NX) via AMA

**Publisher:** FireEye

The [FireEye Network Security (NX)](https://www.fireeye.com/products/network-security.html) data connector provides the capability to ingest FireEye Network Security logs into Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_FireEyeNX_CEFAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/FireEye%20Network%20Security/Data%20Connectors/template_FireEyeNX_CEFAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n