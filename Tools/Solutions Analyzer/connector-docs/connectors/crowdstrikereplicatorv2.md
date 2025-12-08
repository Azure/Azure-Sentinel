# CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)

| | |
|----------|-------|
| **Connector ID** | `CrowdstrikeReplicatorv2` |
| **Publisher** | Crowdstrike |
| **Tables Ingested** | [`ASimAuditEventLogs`](../tables-index.md#asimauditeventlogs), [`ASimAuthenticationEventLogs`](../tables-index.md#asimauthenticationeventlogs), [`ASimAuthenticationEventLogs_CL`](../tables-index.md#asimauthenticationeventlogs_cl), [`ASimDnsActivityLogs`](../tables-index.md#asimdnsactivitylogs), [`ASimFileEventLogs`](../tables-index.md#asimfileeventlogs), [`ASimFileEventLogs_CL`](../tables-index.md#asimfileeventlogs_cl), [`ASimNetworkSessionLogs`](../tables-index.md#asimnetworksessionlogs), [`ASimProcessEventLogs`](../tables-index.md#asimprocesseventlogs), [`ASimProcessEventLogs_CL`](../tables-index.md#asimprocesseventlogs_cl), [`ASimRegistryEventLogs`](../tables-index.md#asimregistryeventlogs), [`ASimRegistryEventLogs_CL`](../tables-index.md#asimregistryeventlogs_cl), [`ASimUserManagementActivityLogs`](../tables-index.md#asimusermanagementactivitylogs), [`ASimUserManagementLogs_CL`](../tables-index.md#asimusermanagementlogs_cl), [`CrowdStrike_Additional_Events_CL`](../tables-index.md#crowdstrike_additional_events_cl), [`CrowdStrike_Secondary_Data_CL`](../tables-index.md#crowdstrike_secondary_data_cl) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [CrowdstrikeReplicatorV2_ConnectorUI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdstrikeReplicatorCLv2/CrowdstrikeReplicatorV2_ConnectorUI.json) |

This connector enables the ingestion of FDR data into Microsoft Sentinel using Azure Functions to support the assessment of potential security risks, analysis of collaboration activities, identification of configuration issues, and other operational insights.<p><span style='color:red; font-weight:bold;'>NOTE:</span></p><div style='margin-left:20px;'><p>1. CrowdStrike FDR license must be available & enabled.</p><p>2. The connector uses a Key & Secret based authentication and is suitable for CrowdStrike Managed buckets.</p><p>3. For environments that use a fully owned AWS S3 bucket, Microsoft recommends using the <strong>CrowdStrike Falcon Data Replicator (AWS S3)</strong> connector.</p></div>

[← Back to Connectors Index](../connectors-index.md)
