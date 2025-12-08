# [DEPRECATED] Cisco Secure Endpoint (AMP)

| | |
|----------|-------|
| **Connector ID** | `CiscoSecureEndpoint` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`CiscoSecureEndpoint_CL`](../tables-index.md#ciscosecureendpoint_cl) |
| **Used in Solutions** | [Cisco Secure Endpoint](../solutions/cisco-secure-endpoint.md) |
| **Connector Definition Files** | [CiscoSecureEndpoint_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Data%20Connectors/CiscoSecureEndpoint_API_FunctionApp.json) |

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://api-docs.amp.cisco.com/api_resources/AuditLog?api_host=api.amp.cisco.com&api_version=v1) and [events](https://api-docs.amp.cisco.com/api_actions/details?api_action=GET+%2Fv1%2Fevents&api_host=api.amp.cisco.com&api_resource=Event&api_version=v1) into Microsoft Sentinel.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

[← Back to Connectors Index](../connectors-index.md)
