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

This solution provides **6 data connector(s)**.

### [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md)

**Publisher:** Microsoft

The [CrowdStrike Data Connector](https://www.crowdstrike.com/) allows ingesting logs from the CrowdStrike API into Microsoft Sentinel. This connector is built on the Microsoft Sentinel Codeless Connector Platform and uses the CrowdStrike API to fetch logs for Alerts, Detections, Hosts, Incidents, and Vulnerabilities. It supports DCR-based ingestion time transformations so that queries can run more efficiently.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CrowdStrikeAlerts` |
| | `CrowdStrikeDetections` |
| | `CrowdStrikeHosts` |
| | `CrowdStrikeIncidents` |
| | `CrowdStrikeVulnerabilities` |
| **Connector Definition Files** | [CrowdStrikeAPI_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeAPI_ccp/CrowdStrikeAPI_Definition.json) |

[→ View full connector details](../connectors/crowdstrikeapiccpdefinition.md)

### [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md)

**Publisher:** CrowdStrike

The [CrowdStrike](https://www.crowdstrike.com/) Falcon Indicators of Compromise connector retrieves the Indicators of Compromise from the Falcon Intel API and uploads them [Microsoft Sentinel Threat Intel](https://learn.microsoft.com/en-us/azure/sentinel/understand-threat-intelligence).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeFalconAdversaryIntelligence/CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json) |

[→ View full connector details](../connectors/crowdstrikefalconadversaryintelligence.md)

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md)

**Publisher:** CrowdStrike

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_Syslog_CrowdStrikeFalconEndpointProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/Connector_Syslog_CrowdStrikeFalconEndpointProtection.json) |

[→ View full connector details](../connectors/crowdstrikefalconendpointprotection.md)

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md)

**Publisher:** CrowdStrike

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CrowdStrikeFalconEndpointProtectionAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/template_CrowdStrikeFalconEndpointProtectionAma.json) |

[→ View full connector details](../connectors/crowdstrikefalconendpointprotectionama.md)

### [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md)

**Publisher:** Microsoft

The Crowdstrike Falcon Data Replicator (S3) connector provides the capability to ingest FDR event datainto Microsoft Sentinel from the AWS S3 bucket where the FDR logs have been streamed. The connector provides ability to get events from Falcon Agents which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector requires an IAM role to be configured on AWS to allow access to the AWS S3 bucket and may not be suitable for environments that leverage CrowdStrike - managed buckets.</p><p>3. For environments that leverage CrowdStrike-managed buckets, please configure the <strong>CrowdStrike Falcon Data Replicator (CrowdStrike-Managed AWS S3)</strong> connector.</p></div>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CrowdStrike_Additional_Events_CL` |
| | `CrowdStrike_Audit_Events_CL` |
| | `CrowdStrike_Auth_Events_CL` |
| | `CrowdStrike_DNS_Events_CL` |
| | `CrowdStrike_File_Events_CL` |
| | `CrowdStrike_Network_Events_CL` |
| | `CrowdStrike_Process_Events_CL` |
| | `CrowdStrike_Registry_Events_CL` |
| | `CrowdStrike_Secondary_Data_CL` |
| | `CrowdStrike_User_Events_CL` |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeS3FDR_ccp/DataConnectorDefinition.json) |

[→ View full connector details](../connectors/crowdstrikefalcons3ccpdefinition.md)

### [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)

**Publisher:** Crowdstrike

This connector enables the ingestion of FDR data into Microsoft Sentinel using Azure Functions to support the assessment of potential security risks, analysis of collaboration activities, identification of configuration issues, and other operational insights.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector uses a Key & Secret based authentication and is suitable for CrowdStrike Managed buckets.</p><p>3. For environments that use a fully owned AWS S3 bucket, Microsoft recommends using the <strong>CrowdStrike Falcon Data Replicator (AWS S3)</strong> connector.</p></div>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ASimAuditEventLogs` |
| | `ASimAuthenticationEventLogs` |
| | `ASimAuthenticationEventLogs_CL` |
| | `ASimDnsActivityLogs` |
| | `ASimFileEventLogs` |
| | `ASimFileEventLogs_CL` |
| | `ASimNetworkSessionLogs` |
| | `ASimProcessEventLogs` |
| | `ASimProcessEventLogs_CL` |
| | `ASimRegistryEventLogs` |
| | `ASimRegistryEventLogs_CL` |
| | `ASimUserManagementActivityLogs` |
| | `ASimUserManagementLogs_CL` |
| | `CrowdStrike_Additional_Events_CL` |
| | `CrowdStrike_Secondary_Data_CL` |
| **Connector Definition Files** | [CrowdstrikeReplicatorV2_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdstrikeReplicatorCLv2/CrowdstrikeReplicatorV2_ConnectorUI.json) |

[→ View full connector details](../connectors/crowdstrikereplicatorv2.md)

## Tables Reference

This solution ingests data into **30 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ASimAuditEventLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimAuthenticationEventLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimAuthenticationEventLogs_CL` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimDnsActivityLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimFileEventLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimFileEventLogs_CL` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimNetworkSessionLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimProcessEventLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimProcessEventLogs_CL` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimRegistryEventLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimRegistryEventLogs_CL` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimUserManagementActivityLogs` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `ASimUserManagementLogs_CL` | [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `CommonSecurityLog` | [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md), [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md) |
| `CrowdStrikeAlerts` | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) |
| `CrowdStrikeDetections` | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) |
| `CrowdStrikeHosts` | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) |
| `CrowdStrikeIncidents` | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) |
| `CrowdStrikeVulnerabilities` | [CrowdStrike API Data Connector (via Codeless Connector Framework)](../connectors/crowdstrikeapiccpdefinition.md) |
| `CrowdStrike_Additional_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md), [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `CrowdStrike_Audit_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_Auth_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_DNS_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_File_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_Network_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_Process_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_Registry_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `CrowdStrike_Secondary_Data_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md), [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md) |
| `CrowdStrike_User_Events_CL` | [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md) |
| `ThreatIntelligenceIndicator` | [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md) |

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

[← Back to Solutions Index](../solutions-index.md)
