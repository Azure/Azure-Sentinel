# Cisco Secure Endpoint

## Solution Information

| | |
|------------------------|-------|
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

### [Cisco Secure Endpoint (via Codeless Connector Framework)](../connectors/ciscosecureendpointlogsccpdefinition.md)

**Publisher:** Microsoft

The Cisco Secure Endpoint (formerly AMP for Endpoints) data connector provides the capability to ingest Cisco Secure Endpoint [audit logs](https://developer.cisco.com/docs/secure-endpoint/auditlog/) and [events](https://developer.cisco.com/docs/secure-endpoint/v1-api-reference-event/) into Microsoft Sentinel.

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
