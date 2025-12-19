# Palo Alto Cortex XDR

| | |
|----------|-------|
| **Connector ID** | `CortexXDRDataConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`PaloAltoCortexXDR_Alerts_CL`](../tables-index.md#paloaltocortexxdr_alerts_cl), [`PaloAltoCortexXDR_Audit_Agent_CL`](../tables-index.md#paloaltocortexxdr_audit_agent_cl), [`PaloAltoCortexXDR_Audit_Management_CL`](../tables-index.md#paloaltocortexxdr_audit_management_cl), [`PaloAltoCortexXDR_Endpoints_CL`](../tables-index.md#paloaltocortexxdr_endpoints_cl), [`PaloAltoCortexXDR_Incidents_CL`](../tables-index.md#paloaltocortexxdr_incidents_cl) |
| **Used in Solutions** | [Cortex XDR](../solutions/cortex-xdr.md), [Palo Alto Cortex XDR CCP](../solutions/palo-alto-cortex-xdr-ccp.md) |
| **Connector Definition Files** | [DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cortex%20XDR/Data%20Connectors/CortexXDR_ccp/DataConnectorDefinition.json) |

The [Palo Alto Cortex XDR](https://cortex-panw.stoplight.io/docs/cortex-xdr/branches/main/09agw06t5dpvw-cortex-xdr-rest-api) data connector allows ingesting logs from the Palo Alto Cortex XDR API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the Palo Alto Cortex XDR API to fetch logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table so that queries don't need to parse it again, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Configuration steps for the Palo Alto Cortex XDR API 
 Follow the instructions to obtain the credentials. you can also follow this [guide](https://cortex-panw.stoplight.io/docs/cortex-xdr/branches/main/3u3j0e7hcx8t1-get-started-with-cortex-xdr-ap-is) to generate API key.
#### 1. Retrieve API URL
   1.1. Log in to the Palo Alto Cortex XDR [**Management Console**] with Admin user credentials
   1.2. In the [**Management Console**], click [**Settings**] -> [**Configurations**] 
   1.3. Under [**Integrations**] click on [**API Keys**].
   1.4. In the [**Settings**] Page click on [**Copy API URL**] in the top right corner.
#### 2. Retrieve API Token
   2.1. Log in to the Palo Alto Cortex XDR [**Management Console**] with Admin user credentials
 2.2. In the [**Management Console**], click [**Settings**] -> [**Configurations**] 
   2.3. Under [**Integrations**] click on [**API Keys**].
   2.4. In the [**Settings**] Page click on [**New Key**] in the top right corner.
   2.5. Choose security level, role, choose Standard and click on [**Generate**]
   2.6. Copy the API Token, once it generated the [**API Token ID**] can be found under the ID column
- **Base API URL**: https://api-example.xdr.au.paloaltonetworks.com
- **API Key ID**: API ID
- **API Token**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
