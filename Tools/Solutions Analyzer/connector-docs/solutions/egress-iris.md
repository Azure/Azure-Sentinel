# Egress Iris

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Egress Software Technologies Ltd |
| **Support Tier** | Partner |
| **Support Link** | [https://support.egress.com](https://support.egress.com) |
| **Categories** | domains |
| **First Published** | 2024-03-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Egress Iris Connector](../connectors/egresssiempolling.md)

**Publisher:** Egress Software Technologies

The Egress Iris connector will allow you to ingest Egress data into Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `DefendAuditData` |
| | `EgressEvents_CL` |
| **Connector Definition Files** | [EgressDataConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Egress%20Iris/Data%20Connectors/EgressDataConnector.json) |

[→ View full connector details](../connectors/egresssiempolling.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DefendAuditData` | [Egress Iris Connector](../connectors/egresssiempolling.md) |
| `EgressEvents_CL` | [Egress Iris Connector](../connectors/egresssiempolling.md) |

[← Back to Solutions Index](../solutions-index.md)
