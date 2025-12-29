# Ubiquiti UniFi

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Ubiquiti_CL` |
| **Connector Definition Files** | [Connector_Ubiquiti_agent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ubiquiti%20UniFi/Data%20Connectors/Connector_Ubiquiti_agent.json) |

[→ View full connector details](../connectors/ubiquitiunifi.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Ubiquiti_CL` | [[Deprecated] Ubiquiti UniFi](../connectors/ubiquitiunifi.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.3       | 04-12-2024                     | Removed Deprecated **Data Connector**                                     |
| 3.0.2       | 09-08-2024                     | Deprecating data connectors                                               |
| 3.0.1       | 16-07-2024                     | Updated the **Analytic rules** for missing TTP					   		   |
| 3.0.0       | 23-01-2024                     | Updated the **Data Connector** by removing preview-tag   				   |

[← Back to Solutions Index](../solutions-index.md)
