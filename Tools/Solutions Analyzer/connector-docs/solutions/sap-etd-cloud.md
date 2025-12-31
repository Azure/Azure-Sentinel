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

This solution provides **1 data connector(s)**:

- [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SAPETDAlerts_CL`](../tables/sapetdalerts-cl.md) | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) | Analytics |
| [`SAPETDInvestigations_CL`](../tables/sapetdinvestigations-cl.md) | [SAP Enterprise Threat Detection, cloud edition](../connectors/sapetdalerts.md) | Analytics |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SAP ETD - Execution of Sensitive Function Module](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Analytic%20Rules/SAPETD-ExecutionofSensitiveFunctionModule.yaml) | Medium | Discovery | - |
| [SAP ETD - Login from unexpected network](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Analytic%20Rules/SAPETD-LoginFromUnexpectedNetwork.yaml) | Medium | Discovery | [`SAPETDAlerts_CL`](../tables/sapetdalerts-cl.md) |
| [SAP ETD - Synch alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Analytic%20Rules/SAPETD-SynchAlerts.yaml) | Medium | - | [`SAPETDAlerts_CL`](../tables/sapetdalerts-cl.md) |
| [SAP ETD - Synch investigations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20ETD%20Cloud/Analytic%20Rules/SAPETD-SynchInvestigations.yaml) | High | - | [`SAPETDInvestigations_CL`](../tables/sapetdinvestigations-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       |  11-09-2025                    | Investigations API Connector added |
| 3.0.2       |  24-06-2025                    | Data connector polling window reduced |
| 3.0.1       |  31-03-2025                    | SAP OData entity change from TriggeringEvents to new NormalizedTriggeringEvents |
| 3.0.0       |  17-02-2025                    | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
