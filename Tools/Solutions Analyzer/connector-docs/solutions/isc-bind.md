# ISC Bind

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] ISC Bind](../connectors/iscbind.md)

**Publisher:** ISC

The [ISC Bind](https://www.isc.org/bind/) connector allows you to easily connect your ISC Bind logs with Microsoft Sentinel. This gives you more insight into your organization's network traffic data, DNS query data, traffic statistics and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_ISCBind.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ISC%20Bind/Data%20Connectors/Connector_Syslog_ISCBind.json) |

[→ View full connector details](../connectors/iscbind.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] ISC Bind](../connectors/iscbind.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 27-12-2024                     |     Removed Deprecated **Data connector**                          |
| 3.0.1       | 24-07-2024                     |     Deprecated Data connectors                                     |
| 3.0.0       | 09-10-2023                     |     Corrected the links in the solution                            |

[← Back to Solutions Index](../solutions-index.md)
