# Onapsis Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Onapsis |
| **Support Tier** | Partner |
| **Support Link** | [https://onapsis.com/company/contact-us](https://onapsis.com/company/contact-us) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Onapsis Platform](../connectors/onapsisplatform.md)

**Publisher:** Onapsis

The Onapsis Connector allows you to export the alarms triggered in the Onapsis Platform into Microsoft Sentinel in real-time. This gives you the ability to monitor the activity on your SAP systems, identify incidents and respond to them quickly.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [OnapsisPlatform.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Onapsis%20Platform/Data%20Connectors/OnapsisPlatform.json) |

[→ View full connector details](../connectors/onapsisplatform.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Onapsis Platform](../connectors/onapsisplatform.md) |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                      |
|---------------|--------------------------------|-----------------------------------------|
| 3.0.0         | 28-06-2024                     | Deprecating data connectors  |
| 2.0.1         | 01-02-2023                     | Updated CreateUi file |

[← Back to Solutions Index](../solutions-index.md)
