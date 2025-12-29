# PDNS Block Data Connector

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Nominet PDNS Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.protectivedns.service.ncsc.gov.uk/pdns](https://www.protectivedns.service.ncsc.gov.uk/pdns) |
| **Categories** | domains |
| **First Published** | 2023-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [PDNS Block Data Connector](../connectors/pdnsblockdataconnector.md)

**Publisher:** Nominet

This application enables you to ingest your PDNS block data into your SIEM tool

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `PDNSBlockData_CL` |
| **Connector Definition Files** | [PDNSBlockDataConnector_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PDNS%20Block%20Data%20Connector/Data%20Connectors/PDNSBlockDataConnector_API_FunctionApp.json) |

[→ View full connector details](../connectors/pdnsblockdataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `PDNSBlockData_CL` | [PDNS Block Data Connector](../connectors/pdnsblockdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
