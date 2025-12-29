# Nasuni

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Nasuni |
| **Support Tier** | Partner |
| **Support Link** | [https://github.com/nasuni-labs/Azure-Sentinel](https://github.com/nasuni-labs/Azure-Sentinel) |
| **Categories** | domains |
| **First Published** | 2023-07-07 |
| **Last Updated** | 2023-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Nasuni Edge Appliance](../connectors/nasuniedgeappliance.md)

**Publisher:** Nasuni

The [Nasuni](https://www.nasuni.com/) connector allows you to easily connect your Nasuni Edge Appliance Notifications and file system audit logs with Microsoft Sentinel. This gives you more insight into activity within your Nasuni infrastructure and improves your security operation capabilities.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Nasuni` |
| | `Syslog` |
| **Connector Definition Files** | [Nasuni%20Data%20Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Nasuni/Data%20Connectors/Nasuni%20Data%20Connector.json) |

[→ View full connector details](../connectors/nasuniedgeappliance.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Nasuni` | [[Deprecated] Nasuni Edge Appliance](../connectors/nasuniedgeappliance.md) |
| `Syslog` | [[Deprecated] Nasuni Edge Appliance](../connectors/nasuniedgeappliance.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       |     03-01-2025                 | Removed Deprecated **Data connector**       |
| 3.0.2       |     18-07-2024                 | Deprecating data connectors                |
| 3.0.1       |     02-08-2023                 | Solution Id and Tier Updated                |
| 3.0.0       |     14-07-2023                 | Initial Solution Release                     |

[← Back to Solutions Index](../solutions-index.md)
