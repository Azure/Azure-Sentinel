# Infoblox Cloud Data Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox BloxOne data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [InfobloxCloudDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Data%20Connectors/InfobloxCloudDataConnector.json) |

[→ View full connector details](../connectors/infobloxclouddataconnector.md)

### [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md)

**Publisher:** Infoblox

The Infoblox Cloud Data Connector allows you to easily connect your Infoblox BloxOne data with Microsoft Sentinel. By connecting your logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_InfobloxCloudDataConnectorAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox%20Cloud%20Data%20Connector/Data%20Connectors/template_InfobloxCloudDataConnectorAMA.json) |

[→ View full connector details](../connectors/infobloxclouddataconnectorama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md), [[Deprecated] Infoblox Cloud Data Connector via Legacy Agent](../connectors/infobloxclouddataconnector.md) |

## Release Notes

| **Version**   | **Date Modified**              | **Change History**                                                     |
|---------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.5         | 06-01-2025                     | Removed Deprecated **Data Connector**                                  |
| 3.0.4         | 12-07-2024                     | Deprecating data connectors                                            |
| 3.0.3         | 30-04-2024                     | Updated package for parser issue fix while reinstall   |
| 3.0.2         | 05-03-2024                     | Updated InfobloxCDC parser to manually parse with extract() rather than dynamically due to slowness   |
| 3.0.1         | 11-09-2023                     | Addition of new Infoblox Cloud Data Connector AMA **Data Connector**   |
| 3.0.0         | 01-08-2023                     | Updated Infoblox logo, **Analytic Rules** Optimization updates. 5 new rules,**Playbooks** 11 new playbooks|
| 2.0.10        | 01-06-2023                     | Bug fixes, Documentation updates                                       |
| 1.0.0         | 01-04-2021                     | Initial Solution Release                                               |

[← Back to Solutions Index](../solutions-index.md)
