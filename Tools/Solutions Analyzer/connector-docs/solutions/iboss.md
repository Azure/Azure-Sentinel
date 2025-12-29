# iboss

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | iboss |
| **Support Tier** | Partner |
| **Support Link** | [https://www.iboss.com/contact-us/](https://www.iboss.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-02-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md)

**Publisher:** iboss

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [iboss_cef.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/iboss_cef.json) |

[→ View full connector details](../connectors/iboss.md)

### [iboss via AMA](../connectors/ibossama.md)

**Publisher:** iboss

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ibossAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/template_ibossAMA.json) |

[→ View full connector details](../connectors/ibossama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md), [iboss via AMA](../connectors/ibossama.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.1.2       | 07-01-2025                     |    Removed Deprecated **Data connector**                           |
| 3.1.1       | 18-09-2024                     |    Updated AMA and legacy OMS connector to use new iboss field     |
| 3.1.0       | 05-09-2024                     |    Updated AMA connector with iboss specific instructions          |
| 3.0.1       | 12-07-2024                     |    Deprecating data connectors                                     |
| 3.0.0       | 20-09-2023                     |	Addition of new Iboss AMA **Data Connector**                    |

[← Back to Solutions Index](../solutions-index.md)
