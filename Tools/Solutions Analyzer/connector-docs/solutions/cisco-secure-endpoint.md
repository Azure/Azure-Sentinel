# Cisco Secure Endpoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-28 |
| **Last Updated** | 2022-02-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[DEPRECATED] Cisco Secure Endpoint (AMP)](../connectors/ciscosecureendpoint.md)

**Publisher:** Cisco

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://api-docs.amp.cisco.com/api_resources/AuditLog?api_host=api.amp.cisco.com&api_version=v1) and [events](https://api-docs.amp.cisco.com/api_actions/details?api_action=GET+%2Fv1%2Fevents&api_host=api.amp.cisco.com&api_resource=Event&api_version=v1) into Microsoft Sentinel.



<p><span style='color:red; font-weight:bold;'>NOTE</span>: This data connector has been deprecated, consider moving to the CCF data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CiscoSecureEndpoint_CL` |
| **Connector Definition Files** | [CiscoSecureEndpoint_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Data%20Connectors/CiscoSecureEndpoint_API_FunctionApp.json) |

[→ View full connector details](../connectors/ciscosecureendpoint.md)

### [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md)

**Publisher:** Microsoft

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://developer.cisco.com/docs/secure-endpoint/auditlog/) and [events](https://developer.cisco.com/docs/secure-endpoint/v1-api-reference-event/) into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CiscoSecureEndpointAuditLogsV2_CL` |
| | `CiscoSecureEndpointEventsV2_CL` |
| **Connector Definition Files** | [CiscoSecureEndpointLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Endpoint/Data%20Connectors/CiscoSecureEndpointLogs_ccp/CiscoSecureEndpointLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/ciscosecureendpointlogsccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CiscoSecureEndpointAuditLogsV2_CL` | [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md) |
| `CiscoSecureEndpointEventsV2_CL` | [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md) |
| `CiscoSecureEndpoint_CL` | [[DEPRECATED] Cisco Secure Endpoint (AMP)](../connectors/ciscosecureendpoint.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                             |
|-------------|-------------------------------|-----------------------------------------------|
| 3.0.2       | 14-08-2025                    | Cisco Secure Endpoint **CCF Connector** moving to GA. |
| 3.0.1       | 23-06-2025                    | Adding a new **CCF Data Connector** - *Cisco Secure Endpoint*  and updated the **Parser** to handle the newly introduced table.  	   |
| 3.0.0       | 28-08-2024                    | Updated the python runtime version to 3.11.    |

[← Back to Solutions Index](../solutions-index.md)
