# Fortinet FortiNDR Cloud

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
