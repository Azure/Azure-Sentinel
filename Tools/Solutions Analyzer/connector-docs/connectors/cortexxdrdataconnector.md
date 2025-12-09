# Palo Alto Cortex XDR

| | |
|----------|-------|
| **Connector ID** | `CortexXDRDataConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PaloAltoCortexXDR_Alerts_CL`](../tables-index.md#paloaltocortexxdr_alerts_cl), [`PaloAltoCortexXDR_Audit_Agent_CL`](../tables-index.md#paloaltocortexxdr_audit_agent_cl), [`PaloAltoCortexXDR_Audit_Management_CL`](../tables-index.md#paloaltocortexxdr_audit_management_cl), [`PaloAltoCortexXDR_Endpoints_CL`](../tables-index.md#paloaltocortexxdr_endpoints_cl), [`PaloAltoCortexXDR_Incidents_CL`](../tables-index.md#paloaltocortexxdr_incidents_cl) |
| **Used in Solutions** | [Cortex XDR](../solutions/cortex-xdr.md), [Palo Alto Cortex XDR CCP](../solutions/palo-alto-cortex-xdr-ccp.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Data%20Connectors/CortexXDR_ccp/DataConnectorDefinition.json) |

The [Palo Alto Cortex XDR](https://cortex-panw.stoplight.io/docs/cortex-xdr/branches/main/09agw06t5dpvw-cortex-xdr-rest-api) data connector allows ingesting logs from the Palo Alto Cortex XDR API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the Palo Alto Cortex XDR API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

[← Back to Connectors Index](../connectors-index.md)
