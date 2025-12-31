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

This solution provides **1 data connector(s)**:

- [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Rubrik_Anomaly_Data_CL`](../tables/rubrik-anomaly-data-cl.md) | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) | Analytics |
| [`Rubrik_Events_Data_CL`](../tables/rubrik-events-data-cl.md) | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) | Analytics |
| [`Rubrik_Ransomware_Data_CL`](../tables/rubrik-ransomware-data-cl.md) | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) | - |
| [`Rubrik_ThreatHunt_Data_CL`](../tables/rubrik-threathunt-data-cl.md) | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) | - |

## Content Items

This solution includes **19 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 17 |
| Analytic Rules | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Rubrik Critical Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Analytic%20Rules/RubrikCriticalAnomaly.yaml) | Medium | Persistence | [`Rubrik_Anomaly_Data_CL`](../tables/rubrik-anomaly-data-cl.md) |
| [Rubrik Threat Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Analytic%20Rules/RubrikThreatMonitoring.yaml) | Medium | Persistence | [`Rubrik_Events_Data_CL`](../tables/rubrik-events-data-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Rubrik Advanced Threat Hunt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikAdvanceThreatHunt/azuredeploy.json) | This playbook fetches the object mapped with incident and starts advance threat hunt. | - |
| [Rubrik Anomaly Analysis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikAnomalyAnalysis/azuredeploy.json) | This playbook queries Rubrik Security Cloud to enrich the Anomaly event with additional information ... | - |
| [Rubrik Anomaly Generate Downloadable Link](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikAnomalyGenerateDownloadableLink/azuredeploy.json) | This playbook will generate downloadable links according to objectType (VMware, Fileset or VolumeGro... | - |
| [Rubrik Anomaly Incident Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikAnomalyIncidentResponse/azuredeploy.json) | This playbook provides an end to end example of the collection of Ransomware Anomaly information fro... | - |
| [Rubrik Data Object Discovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikDataObjectDiscovery/azuredeploy.json) | This playbook queries Rubrik Security Cloud to enrich the incoming event with additional information... | - |
| [Rubrik File Object Context Analysis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikFileObjectContextAnalysis/azuredeploy.json) | This playbook will retrieve policy hits from Rubrik Security Cloud for a given object, for a particu... | - |
| [Rubrik Fileset Ransomware Discovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikFilesetRansomwareDiscovery/azuredeploy.json) | This playbook queries Rubrik Security Cloud to enrich the incoming event with additional information... | - |
| [Rubrik IOC Scan](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikIOCScan/azuredeploy.json) | This playbook interacts with Rubrik Security Cloud to scan backups for specified IOCs. This playbook... | - |
| [Rubrik Poll Async Result](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikPollAsyncResult/azuredeploy.json) | This playbook is used by other playbooks to poll for results from some of the asynchronous API calls... | - |
| [Rubrik Ransomware Discovery and File Recovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikRansomwareDiscoveryAndFileRecovery/azuredeploy.json) | This playbook interacts with Rubrik Security Cloud to (1) optionally preserve evidence by creating a... | - |
| [Rubrik Ransomware Discovery and VM Recovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikRansomwareDiscoveryAndVMRecovery/azuredeploy.json) | This playbook interacts with Rubrik Security Cloud to (1) optionally preserve evidence by creating a... | - |
| [Rubrik Retrieve User Intelligence Information](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikRetrieveUserIntelligenceInformation/azuredeploy.json) | This playbook queries Rubrik Security Cloud to get risk detail and policy hits details for a usernam... | - |
| [Rubrik Turbo Threat Hunt](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikTurboThreatHunt/azuredeploy.json) | This playbook fetches the object mapped with incident and starts turbo threat hunt. | - |
| [Rubrik Update Anomaly Status](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikUpdateAnomalyStatus/azuredeploy.json) | This playbook will resolve or report false positive to unresolved anomaly and update status as resol... | - |
| [Rubrik Update Anomaly Status Via Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikUpdateAnomalyStatusViaIncident/azuredeploy.json) | This playbook queries Rubrik Security Cloud to enrich the Anomaly event with additional information ... | - |
| [Rubrik User Intelligence Analysis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikUserIntelligenceAnalysis/azuredeploy.json) | This playbook queries Rubrik Security Cloud to get user sensitive data and update severity of incide... | - |
| [RubrikWorkloadAnalysis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Playbooks/RubrikWorkloadAnalysis/azuredeploy.json) | This playbook retrieves sensitive IP and Host data to enrich the incident details, and adjusts the i... | - |

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

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
