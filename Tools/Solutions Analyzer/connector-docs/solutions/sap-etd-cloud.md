# SAP ETD Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
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

| Attribute | Value |
|:-------------------------|:---|
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

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       |  11-09-2025                    | Investigations API Connector added |
| 3.0.2       |  24-06-2025                    | Data connector polling window reduced |
| 3.0.1       |  31-03-2025                    | SAP OData entity change from TriggeringEvents to new NormalizedTriggeringEvents |
| 3.0.0       |  17-02-2025                    | Initial Solution Release |

[← Back to Solutions Index](../solutions-index.md)
