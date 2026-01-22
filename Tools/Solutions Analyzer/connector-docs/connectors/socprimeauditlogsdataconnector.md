# SOC Prime Platform Audit Logs Data Connector

| | |
|----------|-------|
| **Connector ID** | `SOCPrimeAuditLogsDataConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SOCPrimeAuditLogs_CL`](../tables-index.md#socprimeauditlogs_cl) |
| **Used in Solutions** | [SOC Prime CCF](../solutions/soc-prime-ccf.md) |
| **Connector Definition Files** | [SOCPrime_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SOC%20Prime%20CCF/Data%20Connectors/SOCPrime_ccp/SOCPrime_DataConnectorDefinition.json) |

The [SOC Prime Audit Logs](https://help.socprime.com/en/articles/6265791-api) data connector allows ingesting logs from the SOC Prime Platform API into Microsoft Sentinel. The data connector is built on Microsoft Sentinel Codeless Connector Platform. It uses the SOC Prime Platform API to fetch SOC Prime platform audit logs and it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview) that parses the received security data into a custom table, thus resulting in better performance.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Configuration steps for the SOC Prime Platform API 
 Follow the instructions to obtain the credentials. you can also follow this [guide](https://help.socprime.com/en/articles/6265791-api#h_8a0d20b204) to generate personal API key.
#### Retrieve API Key
   1. Log in to the SOC Prime Platform
 2. Click [**Account**] icon -> [**Platform Settings**] -> [**API**] 
   3. Click [**Add New Key**] 
   4. In the modal that appears give your key a meaningful name, set expiration date and product APIs the key provides access to 
   5. Click on [**Generate**] 
   6. Copy the key and save it in a safe place. You won't be able to view it again once you close this modal 
- **SOC Prime API Key**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
