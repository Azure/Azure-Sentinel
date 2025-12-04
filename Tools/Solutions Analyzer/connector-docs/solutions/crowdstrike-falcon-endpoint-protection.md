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

### [CrowdStrike Falcon Adversary Intelligence ](../connectors/crowdstrikefalconadversaryintelligence.md)

**Publisher:** CrowdStrike

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via Legacy Agent](../connectors/crowdstrikefalconendpointprotection.md)

**Publisher:** CrowdStrike

### [[Deprecated] CrowdStrike Falcon Endpoint Protection via AMA](../connectors/crowdstrikefalconendpointprotectionama.md)

**Publisher:** CrowdStrike

### [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](../connectors/crowdstrikefalcons3ccpdefinition.md)

**Publisher:** Microsoft

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

[← Back to Solutions Index](../solutions-index.md)
