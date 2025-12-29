# Fortinet FortiNDR Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Fortinet |
| **Support Tier** | Partner |
| **Support Link** | [https://www.fortinet.com/support](https://www.fortinet.com/support) |
| **Categories** | domains |
| **First Published** | 2024-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md)

**Publisher:** Fortinet

The Fortinet FortiNDR Cloud data connector provides the capability to ingest [Fortinet FortiNDR Cloud](https://docs.fortinet.com/product/fortindr-cloud) data into Microsoft Sentinel using the FortiNDR Cloud API

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `FncEventsDetections_CL` |
| | `FncEventsObservation_CL` |
| | `FncEventsSuricata_CL` |
| **Connector Definition Files** | [FortinetFortiNdrCloud_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiNDR%20Cloud/Data%20Connectors/FortinetFortiNdrCloud_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/fortinetfortindrclouddataconnector.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `FncEventsDetections_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |
| `FncEventsObservation_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |
| `FncEventsSuricata_CL` | [Fortinet FortiNDR Cloud](../connectors/fortinetfortindrclouddataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                    |
|-------------|--------------------------------|-------------------------------------------------------|
| 3.0.3       | 05-05-2025                     | Use Flex Consumption plan to hold Data Connector      |
| 3.0.2       | 30-09-2024                     | Show mitre attack ids and link to detection rule page |
| 3.0.1       | 31-05-2024                     | Replace Metastream with FortiNDR Cloud API            |
| 3.0.0       | 29-02-2024                     | Initial Solution Release                              |

[← Back to Solutions Index](../solutions-index.md)
