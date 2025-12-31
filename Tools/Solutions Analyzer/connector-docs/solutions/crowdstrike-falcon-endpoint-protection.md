# CrowdStrike Falcon Endpoint Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection) |

## Data Connectors

This solution provides **6 data connector(s)**:

- [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md)
- [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md)
- [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md)
- [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md)
- [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md)
- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)

## Tables Reference

This solution uses **30 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ASimAuditEventLogs`](../tables/asimauditeventlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimAuthenticationEventLogs`](../tables/asimauthenticationeventlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimAuthenticationEventLogs_CL`](../tables/asimauthenticationeventlogs-cl.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimFileEventLogs`](../tables/asimfileeventlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimFileEventLogs_CL`](../tables/asimfileeventlogs-cl.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimProcessEventLogs`](../tables/asimprocesseventlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimProcessEventLogs_CL`](../tables/asimprocesseventlogs-cl.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimRegistryEventLogs`](../tables/asimregistryeventlogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimRegistryEventLogs_CL`](../tables/asimregistryeventlogs-cl.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimUserManagementActivityLogs`](../tables/asimusermanagementactivitylogs.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`ASimUserManagementLogs_CL`](../tables/asimusermanagementlogs-cl.md) | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md), [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md) | Analytics, Workbooks |
| [`CrowdStrikeAlerts`](../tables/crowdstrikealerts.md) | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) | - |
| [`CrowdStrikeDetections`](../tables/crowdstrikedetections.md) | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) | - |
| [`CrowdStrikeHosts`](../tables/crowdstrikehosts.md) | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) | - |
| [`CrowdStrikeIncidents`](../tables/crowdstrikeincidents.md) | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) | - |
| [`CrowdStrikeVulnerabilities`](../tables/crowdstrikevulnerabilities.md) | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) | - |
| [`CrowdStrike_Additional_Events_CL`](../tables/crowdstrike-additional-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md), [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`CrowdStrike_Audit_Events_CL`](../tables/crowdstrike-audit-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_Auth_Events_CL`](../tables/crowdstrike-auth-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_DNS_Events_CL`](../tables/crowdstrike-dns-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_File_Events_CL`](../tables/crowdstrike-file-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_Network_Events_CL`](../tables/crowdstrike-network-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_Process_Events_CL`](../tables/crowdstrike-process-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_Registry_Events_CL`](../tables/crowdstrike-registry-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`CrowdStrike_Secondary_Data_CL`](../tables/crowdstrike-secondary-data-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md), [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) | - |
| [`CrowdStrike_User_Events_CL`](../tables/crowdstrike-user-events-cl.md) | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) | - |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md) | - |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 4 |
| Playbooks | 3 |
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Critical Severity Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Analytic%20Rules/CriticalSeverityDetection.yaml) | High | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Critical or High Severity Detections by User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Analytic%20Rules/CriticalOrHighSeverityDetectionsByUser.yaml) | High | - | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CrowdStrikeFalconEndpointProtection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Workbooks/CrowdStrikeFalconEndpointProtection.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Crowdstrike API authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Playbooks/CrowdStrike_Base/azuredeploy.json) | This is Crowdstrike base template which is used to generate access token and this is used in actual ... | - |
| [Endpoint enrichment - Crowdstrike](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Playbooks/CrowdStrike_Enrichment_GetDeviceInformation/azuredeploy.json) | When a new Microsoft Sentinel incident is created, this playbook gets triggered and performs below a... | - |
| [Isolate endpoint - Crowdstrike](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Playbooks/CrowdStrike_ContainHost/azuredeploy.json) | When a new Microsoft Sentinel incident is created, this playbook gets triggered and performs below a... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CrowdStrikeFalconEventStream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeFalconEventStream.yaml) | - | - |
| [CrowdStrikeReplicator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeReplicator.yaml) | - | - |
| [CrowdStrikeReplicatorV2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeReplicatorV2.yaml) | - | - |
| [CrowdStrikeReplicator_future](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Parsers/CrowdStrikeReplicator_future.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.1.9       | 17-12-2025                     | Updated *CrowdStrike API Data Connector* Enhance API configuration instructions with link |
| 3.1.8       | 08-12-2025                     | Updated *CrowdStrike API Data Connector* to fix rate limit exceptions by introducing retry logic. |
| 3.1.7       | 12-11-2025                     | Updated *CrowdStrike API Data Connector* to fix rate limit exceptions |
| 3.1.6       | 23-10-2025                     | Updated *CrowdStrike API Data Connector* to fix deprecated detections API issues |
| 3.1.5       | 22-08-2025                     | Updated *CrowdStrike API Data Connector* to fix duplicate logs issues |
| 3.1.4       | 04-07-2025                     | Added new **CCF Connector** to the Solution *CrowdStrike API Data Connector*.<br/>Removed *Crowdstrike Falcon Data Replicator* - Function App **Data Connector**.<br/>Updated Connectors description. |
| 3.1.3       | 24-06-2025                     | Removed "DEPRECATED" label from the *Crowdstrike Falcon Data Replicator V2* - **Data connector**. <br/> Updated Solution description.                                      |
| 3.1.2       | 03-06-2025                     | Crowdstrike Falcon S3 **CCF connector** moving to GA.                                    |
| 3.1.1       | 08-05-2025                     | Added preview tag to **CCP Connector**.                                    |
| 3.1.0       | 11-03-2025                     | Added new CCP **Data Connector** to the Solution.                                    |
| 3.0.10      | 15-01-2025                     | Resolve **Workbook** data type dependency issue.                                    |
| 3.0.9       | 12-11-2024                     | Removed deprecated **Data Connectors**.                                             |
|             |                                | Updated the python runtime version to 3.11 in **Data Connector** Function App.                                                                               |
| 3.0.8 	  | 10-07-2024 					   | Deprecated **Data Connector**. 										            |
| 3.0.7       | 20-06-2024                     | Shortlinks updated for **Data Connector** CrowdStrike Falcon Indicators of Compromise.                   |
| 3.0.6       | 06-06-2024                     | Renamed **Data Connector** *CrowdStrike Falcon Indicators of Compromise* to *CrowdStrike Falcon Adversary Intelligence*. |
| 3.0.5       | 30-05-2024                     | Added new Function App **Data Connector** CrowdStrike Falcon Indicators of Compromise.                   |
| 3.0.4       | 03-05-2024                     | Fixed **Parser** issue for Parser name and ParentID mismatch.                   |
| 3.0.3       | 10-04-2024                     | Added Azure Deploy button for government portal deployments.                    |
| 3.0.2       | 14-02-2024                     | Addition of new CrowdStrike Falcon Endpoint Protection AMA **Data Connector**.  |
| 3.0.1       | 31-01-2024                     | **Data Connector**[Crowdstrike Falcon Data Replicator V2] globally available.   |
| 3.0.0       | 28-07-2023                     | New **Data Connector** added.                                                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
