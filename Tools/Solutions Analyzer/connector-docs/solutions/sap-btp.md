# SAP BTP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2023-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP BTP](../connectors/sapbtpauditevents.md)

**Publisher:** Microsoft

SAP Business Technology Platform (SAP BTP) brings together data management, analytics, artificial intelligence, application development, automation, and integration in one, unified environment.

| | |
|--------------------------|---|
| **Tables Ingested** | `SAPBTPAuditLog_CL` |
| **Connector Definition Files** | [SAPBTP_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Data%20Connectors/SAPBTPPollerConnector/SAPBTP_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/sapbtpauditevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SAPBTPAuditLog_CL` | [SAP BTP](../connectors/sapbtpauditevents.md) |

[← Back to Solutions Index](../solutions-index.md)
