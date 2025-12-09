# Juniper SRX

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Juniper SRX](../connectors/junipersrx.md)

**Publisher:** Juniper

The [Juniper SRX](https://www.juniper.net/us/en/products-services/security/srx-series/) connector allows you to easily connect your Juniper SRX logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Connector_Syslog_JuniperSRX.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Juniper%20SRX/Data%20Connectors/Connector_Syslog_JuniperSRX.json) |

[→ View full connector details](../connectors/junipersrx.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Juniper SRX](../connectors/junipersrx.md) |

[← Back to Solutions Index](../solutions-index.md)
