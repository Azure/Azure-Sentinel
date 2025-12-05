# SINEC Security Guard

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Siemens AG |
| **Support Tier** | Partner |
| **Support Link** | [https://siemens.com/sinec-security-guard](https://siemens.com/sinec-security-guard) |
| **Categories** | domains,verticals |
| **First Published** | 2024-07-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SINEC Security Guard](../connectors/ssg.md)

**Publisher:** Siemens AG

The SINEC Security Guard solution for Microsoft Sentinel allows you to ingest security events of your industrial networks from the [SINEC Security Guard](https://siemens.com/sinec-security-guard) into Microsoft Sentinel

| | |
|--------------------------|---|
| **Tables Ingested** | `SINECSecurityGuard_CL` |
| **Connector Definition Files** | [data_connector_GenericUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SINEC%20Security%20Guard/Data%20Connectors/data_connector_GenericUI.json) |

[→ View full connector details](../connectors/ssg.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SINECSecurityGuard_CL` | [SINEC Security Guard](../connectors/ssg.md) |

[← Back to Solutions Index](../solutions-index.md)
