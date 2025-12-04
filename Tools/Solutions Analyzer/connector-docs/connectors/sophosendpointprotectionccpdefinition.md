# Sophos Endpoint Protection (using REST API)

| | |
|----------|-------|
| **Connector ID** | `SophosEndpointProtectionCCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SophosEPAlerts_CL`](../tables-index.md#sophosepalerts_cl), [`SophosEPEvents_CL`](../tables-index.md#sophosepevents_cl) |
| **Used in Solutions** | [Sophos Endpoint Protection](../solutions/sophos-endpoint-protection.md) |
| **Connector Definition Files** | [SophosEP_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection/Data%20Connectors/SophosEP_ccp/SophosEP_DataConnectorDefinition.json) |

The [Sophos Endpoint Protection](https://www.sophos.com/en-us/products/endpoint-antivirus.aspx) data connector provides the capability to ingest [Sophos events](https://developer.sophos.com/docs/siem-v1/1/routes/events/get) and [Sophos alerts](https://developer.sophos.com/docs/siem-v1/1/routes/alerts/get) into Microsoft Sentinel. Refer to [Sophos Central Admin documentation](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/concepts/Logs.html) for more information.

[← Back to Connectors Index](../connectors-index.md)
