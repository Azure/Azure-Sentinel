# Ubiquiti UniFi

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Ubiquiti UniFi](../connectors/ubiquitiunifi.md)

**Publisher:** Ubiquiti

The [Ubiquiti UniFi](https://www.ui.com/) data connector provides the capability to ingest [Ubiquiti UniFi firewall, dns, ssh, AP events](https://help.ui.com/hc/en-us/articles/204959834-UniFi-How-to-View-Log-Files) into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `Ubiquiti_CL` |
| **Connector Definition Files** | [Connector_Ubiquiti_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Data%20Connectors/Connector_Ubiquiti_agent.json) |

[→ View full connector details](../connectors/ubiquitiunifi.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Ubiquiti_CL` | [[Deprecated] Ubiquiti UniFi](../connectors/ubiquitiunifi.md) |

[← Back to Solutions Index](../solutions-index.md)
