# iboss

## Solution Information

| | |
|------------------------|-------|
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

### [iboss via AMA](../connectors/ibossama.md)

**Publisher:** iboss

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ibossAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/template_ibossAMA.json) |

[→ View full connector details](../connectors/ibossama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md), [iboss via AMA](../connectors/ibossama.md) |

[← Back to Solutions Index](../solutions-index.md)
