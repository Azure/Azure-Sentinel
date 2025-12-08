# Infoblox Cloud Data Connector

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](../connectors/infobloxclouddataconnector.md)

**Publisher:** Infoblox

### [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md)

**Publisher:** Infoblox

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox BloxOne data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_InfobloxCloudDataConnectorAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Data%20Connectors/template_InfobloxCloudDataConnectorAMA.json) |

[→ View full connector details](../connectors/infobloxclouddataconnectorama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md), [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](../connectors/infobloxclouddataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
