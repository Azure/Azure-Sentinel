# CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeFalconS3CCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CrowdStrike_Additional_Events_CL`](../tables-index.md#crowdstrike_additional_events_cl), [`CrowdStrike_Audit_Events_CL`](../tables-index.md#crowdstrike_audit_events_cl), [`CrowdStrike_Auth_Events_CL`](../tables-index.md#crowdstrike_auth_events_cl), [`CrowdStrike_DNS_Events_CL`](../tables-index.md#crowdstrike_dns_events_cl), [`CrowdStrike_File_Events_CL`](../tables-index.md#crowdstrike_file_events_cl), [`CrowdStrike_Network_Events_CL`](../tables-index.md#crowdstrike_network_events_cl), [`CrowdStrike_Process_Events_CL`](../tables-index.md#crowdstrike_process_events_cl), [`CrowdStrike_Registry_Events_CL`](../tables-index.md#crowdstrike_registry_events_cl), [`CrowdStrike_Secondary_Data_CL`](../tables-index.md#crowdstrike_secondary_data_cl), [`CrowdStrike_User_Events_CL`](../tables-index.md#crowdstrike_user_events_cl) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeS3FDR_ccp/DataConnectorDefinition.json) |

The Crowdstrike Falcon Data Replicator (S3) connector provides the capability to ingest FDR event datainto Microsoft Sentinel from the AWS S3 bucket where the FDR logs have been streamed. The connector provides ability to get events from Falcon Agents which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector requires an IAM role to be configured on AWS to allow access to the AWS S3 bucket and may not be suitable for environments that leverage CrowdStrike - managed buckets.</p><p>3. For environments that leverage CrowdStrike-managed buckets, please configure the <strong>CrowdStrike Falcon Data Replicator (CrowdStrike-Managed AWS S3)</strong> connector.</p></div>

[← Back to Connectors Index](../connectors-index.md)
