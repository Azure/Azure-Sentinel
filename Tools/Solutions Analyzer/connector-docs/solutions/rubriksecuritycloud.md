# RubrikSecurityCloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Rubrik |
| **Support Tier** | Partner |
| **Support Link** | [https://support.rubrik.com](https://support.rubrik.com) |
| **Categories** | domains |
| **First Published** | 2022-07-19 |
| **Last Updated** | 2025-07-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md)

**Publisher:** Rubrik, Inc

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik's Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Rubrik_Anomaly_Data_CL` |
| | `Rubrik_Events_Data_CL` |
| | `Rubrik_Ransomware_Data_CL` |
| | `Rubrik_ThreatHunt_Data_CL` |
| **Connector Definition Files** | [RubrikWebhookEvents_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Data%20Connectors/RubrikWebhookEvents/RubrikWebhookEvents_FunctionApp.json) |

[→ View full connector details](../connectors/rubriksecuritycloudazurefunctions.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Rubrik_Anomaly_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_Events_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_Ransomware_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_ThreatHunt_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.5.1       | 05-11-2025                     | Updated API Host Name default value in playbooks and custom connector |
| 3.5.0       | 25-07-2025                     | Added RubrikTurboThreatHunt and RubrikAdvanceThreatHunt playbooks. RubrikThreatMonitoring and RubrikCriticalAnomaly Analytic Rules also added.
| 3.4.0       | 07-04-2025                     | Added RubrikUpdateAnomalyStatusViaIncident and RubrikUpdateAnomalyStatus playbook. Enhanced RubrikAnomalyAnalysis playbook. Added User-Agent in every API call of each playbook. Removed policy creation resources from data connector Arm template.
| 3.3.0       | 19-11-2024                     | Added one new Playbook(RubrikWorkloadAnalysis) and updated the RubrikWebhookEvents Data Connector to add a new Orchestrator for Rubrik Events.
| 3.2.1       | 11-11-2024                     | Fixed the issue of Custom Connector id parameter in RubrikRansomwareDiscoveryAndVmRecovery playbook. |
| 3.2.0       | 24-02-2024                     | Added 3 new Playbooks(RubrikFileObjectContextAnalysis, RubrikUserIntelligenceAnalysis, RubrikRetrieveUserIntelligenceInformation) for FileObject and User, fixed clusterLocation issue of Collect_IOC_Scan_Data adaptive card in RubrikRansomwareDiscoveryAndVmRecovery playbook and updated python packages to fix vulnerability CVE-2023-50782 of cryptography module. Enhanced Anomaly Analysis playbook and added RubrikAnomalyGenerateDownloadableLink playbook. |
| 3.1.0       | 20-10-2023                     | Updated the **DataConnector** code by implementing Durable Function App. |
| 3.0.0       | 14-07-2023                     | Updated the title in such a way that user can identify the adaptive card based on incident. |

[← Back to Solutions Index](../solutions-index.md)
