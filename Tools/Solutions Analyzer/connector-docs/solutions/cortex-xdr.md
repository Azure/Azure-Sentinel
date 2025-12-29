# Cortex XDR

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md)

**Publisher:** Microsoft

The [Palo Alto Cortex XDR](https://cortex-panw.stoplight.io/docs/cortex-xdr/branches/main/09agw06t5dpvw-cortex-xdr-rest-api) data connector allows ingesting logs from the Palo Alto Cortex XDR API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the Palo Alto Cortex XDR API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PaloAltoCortexXDR_Alerts_CL` |
| | `PaloAltoCortexXDR_Audit_Agent_CL` |
| | `PaloAltoCortexXDR_Audit_Management_CL` |
| | `PaloAltoCortexXDR_Endpoints_CL` |
| | `PaloAltoCortexXDR_Incidents_CL` |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Data%20Connectors/CortexXDR_ccp/DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cortexxdrdataconnector.md)

### [Cortex XDR - Incidents](../connectors/cortexxdrincidents.md)

**Publisher:** DEFEND Ltd.

Custom Data connector from DEFEND to utilise the Cortex API to ingest incidents from Cortex XDR platform into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PaloAltoCortexXDR_Incidents_CL` |
| **Connector Definition Files** | [CortexXDR_DataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Data%20Connectors/CortexXDR_DataConnector.json) |

[→ View full connector details](../connectors/cortexxdrincidents.md)

## Tables Reference

This solution ingests data into **5 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PaloAltoCortexXDR_Alerts_CL` | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) |
| `PaloAltoCortexXDR_Audit_Agent_CL` | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) |
| `PaloAltoCortexXDR_Audit_Management_CL` | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) |
| `PaloAltoCortexXDR_Endpoints_CL` | [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) |
| `PaloAltoCortexXDR_Incidents_CL` | [Cortex XDR - Incidents](../connectors/cortexxdrincidents.md), [Palo Alto Cortex XDR](../connectors/cortexxdrdataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.0       | 28-07-2023                     | Initial Solution Release                                                 |

[← Back to Solutions Index](../solutions-index.md)
