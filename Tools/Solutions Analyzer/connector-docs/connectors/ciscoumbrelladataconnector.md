# Cisco Cloud Security

| | |
|----------|-------|
| **Connector ID** | `CiscoUmbrellaDataConnector` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`Cisco_Umbrella_audit_CL`](../tables-index.md#cisco_umbrella_audit_cl), [`Cisco_Umbrella_cloudfirewall_CL`](../tables-index.md#cisco_umbrella_cloudfirewall_cl), [`Cisco_Umbrella_dlp_CL`](../tables-index.md#cisco_umbrella_dlp_cl), [`Cisco_Umbrella_dns_CL`](../tables-index.md#cisco_umbrella_dns_cl), [`Cisco_Umbrella_fileevent_CL`](../tables-index.md#cisco_umbrella_fileevent_cl), [`Cisco_Umbrella_firewall_CL`](../tables-index.md#cisco_umbrella_firewall_cl), [`Cisco_Umbrella_intrusion_CL`](../tables-index.md#cisco_umbrella_intrusion_cl), [`Cisco_Umbrella_ip_CL`](../tables-index.md#cisco_umbrella_ip_cl), [`Cisco_Umbrella_proxy_CL`](../tables-index.md#cisco_umbrella_proxy_cl), [`Cisco_Umbrella_ravpnlogs_CL`](../tables-index.md#cisco_umbrella_ravpnlogs_cl), [`Cisco_Umbrella_ztaflow_CL`](../tables-index.md#cisco_umbrella_ztaflow_cl), [`Cisco_Umbrella_ztna_CL`](../tables-index.md#cisco_umbrella_ztna_cl) |
| **Used in Solutions** | [CiscoUmbrella](../solutions/ciscoumbrella.md) |
| **Connector Definition Files** | [CiscoUmbrella_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Data%20Connectors/CiscoUmbrella_API_FunctionApp.json) |

The Cisco Cloud Security solution for Microsoft Sentinel enables you to ingest [Cisco Secure Access](https://docs.sse.cisco.com/sse-user-guide/docs/welcome-cisco-secure-access) and [Cisco Umbrella](https://docs.umbrella.com/umbrella-user-guide/docs/getting-started) [logs](https://docs.sse.cisco.com/sse-user-guide/docs/manage-your-logs) stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Cloud Security log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.

[← Back to Connectors Index](../connectors-index.md)
