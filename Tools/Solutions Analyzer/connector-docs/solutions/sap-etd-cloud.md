# SAP ETD Cloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://help.sap.com/docs/SAP_ENTERPRISE_THREAT_DETECTION_CLOUD_EDITION](https://help.sap.com/docs/SAP_ENTERPRISE_THREAT_DETECTION_CLOUD_EDITION) |
| **Categories** | domains |
| **First Published** | 2025-02-17 |
| **Last Updated** | 2025-09-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md)

**Publisher:** SAP

The SAP Enterprise Threat Detection, cloud edition (ETD) data connector enables ingestion of security alerts from ETD into Microsoft Sentinel, supporting cross-correlation, alerting, and threat hunting.

| | |
|--------------------------|---|
| **Tables Ingested** | `SAPETDAlerts_CL` |
| | `SAPETDInvestigations_CL` |
| **Connector Definition Files** | [SAPETD_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Data%20Connectors/SAPETD_PUSH_CCP/SAPETD_connectorDefinition.json) |

[→ View full connector details](../connectors/sapetdalerts.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SAPETDAlerts_CL` | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) |
| `SAPETDInvestigations_CL` | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) |

[← Back to Solutions Index](../solutions-index.md)
