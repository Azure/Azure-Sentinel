# PingFederate

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md)

**Publisher:** Ping Identity

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_CEF_PingFederate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/Connector_CEF_PingFederate.json) |

[→ View full connector details](../connectors/pingfederate.md)

### [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md)

**Publisher:** Ping Identity

The [PingFederate](https://www.pingidentity.com/en/software/pingfederate.html) data connector provides the capability to ingest [PingFederate events](https://docs.pingidentity.com/bundle/pingfederate-102/page/lly1564002980532.html) into Microsoft Sentinel. Refer to [PingFederate documentation](https://docs.pingidentity.com/bundle/pingfederate-102/page/tle1564002955874.html) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_PingFederateAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Data%20Connectors/template_PingFederateAMA.json) |

[→ View full connector details](../connectors/pingfederateama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md), [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 22-11-2024                     |    Removed Deprecated **Data Connectors**                           |
| 3.0.1 	  | 12-07-2024 					   |    Deprecated **Data Connector** 									|
| 3.0.0       | 04-09-2023                     |	Addition of new PingFederate AMA **Data Connector**             |

[← Back to Solutions Index](../solutions-index.md)
