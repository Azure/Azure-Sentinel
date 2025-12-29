# Blackberry CylancePROTECT

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Blackberry CylancePROTECT](../connectors/blackberrycylanceprotect.md)

**Publisher:** Blackberry

The [Blackberry CylancePROTECT](https://www.blackberry.com/us/en/products/blackberry-protect) connector allows you to easily connect your CylancePROTECT logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [template_BlackberryCylancePROTECT.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Blackberry%20CylancePROTECT/Data%20Connectors/template_BlackberryCylancePROTECT.JSON) |

[→ View full connector details](../connectors/blackberrycylanceprotect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Blackberry CylancePROTECT](../connectors/blackberrycylanceprotect.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.1       | 23-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.0       | 18-07-2024                     | Deprecating data connectors                 |

[← Back to Solutions Index](../solutions-index.md)
