# CrowdStrike Falcon Endpoint Protection

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeFalconAdversaryIntelligence/CrowdStrikeFalconAdversaryIntelligence_FunctionApp.json) |

[→ View full connector details](../connectors/crowdstrikefalconadversaryintelligence.md)

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md)

**Publisher:** CrowdStrike

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_Syslog_CrowdStrikeFalconEndpointProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/Connector_Syslog_CrowdStrikeFalconEndpointProtection.json) |

[→ View full connector details](../connectors/crowdstrikefalconendpointprotection.md)

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md)

**Publisher:** CrowdStrike

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CrowdStrikeFalconEndpointProtectionAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/template_CrowdStrikeFalconEndpointProtectionAma.json) |

[→ View full connector details](../connectors/crowdstrikefalconendpointprotectionama.md)

### [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md)

**Publisher:** Microsoft

The Crowdstrike Falcon Data Replicator (S3) connector provides the capability to ingest FDR event datainto Microsoft Sentinel from the AWS S3 bucket where the FDR logs have been streamed. The connector provides ability to get events from Falcon Agents which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector requires an IAM role to be configured on AWS to allow access to the AWS S3 bucket and may not be suitable for environments that leverage CrowdStrike - managed buckets.</p><p>3. For environments that leverage CrowdStrike-managed buckets, please configure the <strong>CrowdStrike Falcon Data Replicator (CrowdStrike-Managed AWS S3)</strong> connector.</p></div>

| | |
|--------------------------|---|
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

| | |
|--------------------------|---|
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
| `ASimAuditEventLogs` | 1 connector(s) |
| `ASimAuthenticationEventLogs` | 1 connector(s) |
| `ASimAuthenticationEventLogs_CL` | 1 connector(s) |
| `ASimDnsActivityLogs` | 1 connector(s) |
| `ASimFileEventLogs` | 1 connector(s) |
| `ASimFileEventLogs_CL` | 1 connector(s) |
| `ASimNetworkSessionLogs` | 1 connector(s) |
| `ASimProcessEventLogs` | 1 connector(s) |
| `ASimProcessEventLogs_CL` | 1 connector(s) |
| `ASimRegistryEventLogs` | 1 connector(s) |
| `ASimRegistryEventLogs_CL` | 1 connector(s) |
| `ASimUserManagementActivityLogs` | 1 connector(s) |
| `ASimUserManagementLogs_CL` | 1 connector(s) |
| `CommonSecurityLog` | 2 connector(s) |
| `CrowdStrikeAlerts` | 1 connector(s) |
| `CrowdStrikeDetections` | 1 connector(s) |
| `CrowdStrikeHosts` | 1 connector(s) |
| `CrowdStrikeIncidents` | 1 connector(s) |
| `CrowdStrikeVulnerabilities` | 1 connector(s) |
| `CrowdStrike_Additional_Events_CL` | 2 connector(s) |
| `CrowdStrike_Audit_Events_CL` | 1 connector(s) |
| `CrowdStrike_Auth_Events_CL` | 1 connector(s) |
| `CrowdStrike_DNS_Events_CL` | 1 connector(s) |
| `CrowdStrike_File_Events_CL` | 1 connector(s) |
| `CrowdStrike_Network_Events_CL` | 1 connector(s) |
| `CrowdStrike_Process_Events_CL` | 1 connector(s) |
| `CrowdStrike_Registry_Events_CL` | 1 connector(s) |
| `CrowdStrike_Secondary_Data_CL` | 2 connector(s) |
| `CrowdStrike_User_Events_CL` | 1 connector(s) |
| `ThreatIntelligenceIndicator` | CrowdStrike Falcon Adversary Intelligence  |

[← Back to Solutions Index](../solutions-index.md)
