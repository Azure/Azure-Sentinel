# SAP S4 Cloud Public Edition

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://api.sap.com/api/SecurityAuditLog_ODataService/overview](https://api.sap.com/api/SecurityAuditLog_ODataService/overview) |
| **Categories** | domains |
| **First Published** | 2025-09-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP S/4HANA Cloud Public Edition](../connectors/saps4publicalerts.md)

**Publisher:** SAP

The SAP S/4HANA Cloud Public Edition (GROW with SAP) data connector enables ingestion of SAP's security audit log into the Microsoft Sentinel Solution for SAP, supporting cross-correlation, alerting, and threat hunting. Looking for alternative authentication mechanisms? See [here](https://github.com/Azure-Samples/Sentinel-For-SAP-Community/tree/main/integration-artifacts).

| | |
|--------------------------|---|
| **Tables Ingested** | `ABAPAuditLog` |
| **Connector Definition Files** | [SAPS4Public_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition/Data%20Connectors/SAPS4PublicPollerConnector/SAPS4Public_connectorDefinition.json) |

[→ View full connector details](../connectors/saps4publicalerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABAPAuditLog` | [SAP S/4HANA Cloud Public Edition](../connectors/saps4publicalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
