# CYFIRMA Compromised Accounts

| | |
|----------|-------|
| **Connector ID** | `CyfirmaCompromisedAccountsDataConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CyfirmaCompromisedAccounts_CL`](../tables-index.md#cyfirmacompromisedaccounts_cl) |
| **Used in Solutions** | [Cyfirma Compromised Accounts](../solutions/cyfirma-compromised-accounts.md) |
| **Connector Definition Files** | [CyfirmaCompAcc_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts/Data%20Connectors/CyfirmaCompromisedAccounts_ccp/CyfirmaCompAcc_DataConnectorDefinition.json) |

The CYFIRMA Compromised Accounts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR/DeTCT API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[← Back to Connectors Index](../connectors-index.md)
