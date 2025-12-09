# Watchguard Firebox

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | WatchGuard |
| **Support Tier** | Partner |
| **Support Link** | [https://www.watchguard.com/wgrd-support/contact-support](https://www.watchguard.com/wgrd-support/contact-support) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md)

**Publisher:** WatchGuard Technologies

WatchGuard Firebox (https://www.watchguard.com/wgrd-products/firewall-appliances and https://www.watchguard.com/wgrd-products/cloud-and-virtual-firewalls) is security products/firewall-appliances. Watchguard Firebox will send syslog to Watchguard Firebox collector agent.The agent then sends the message to the workspace.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_syslog_WatchGuardFirebox.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Watchguard%20Firebox/Data%20Connectors/Connector_syslog_WatchGuardFirebox.json) |

[→ View full connector details](../connectors/watchguardfirebox.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] WatchGuard Firebox](../connectors/watchguardfirebox.md) |

[← Back to Solutions Index](../solutions-index.md)
