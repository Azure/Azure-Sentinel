# Netskope Data Connector

| | |
|----------|-------|
| **Connector ID** | `NetskopeDataConnector` |
| **Publisher** | Netskope |
| **Tables Ingested** | [`Netskope_WebTx_metrics_CL`](../tables-index.md#netskope_webtx_metrics_cl), [`alertscompromisedcredentialdata_CL`](../tables-index.md#alertscompromisedcredentialdata_cl), [`alertsctepdata_CL`](../tables-index.md#alertsctepdata_cl), [`alertsdlpdata_CL`](../tables-index.md#alertsdlpdata_cl), [`alertsmalsitedata_CL`](../tables-index.md#alertsmalsitedata_cl), [`alertsmalwaredata_CL`](../tables-index.md#alertsmalwaredata_cl), [`alertspolicydata_CL`](../tables-index.md#alertspolicydata_cl), [`alertsquarantinedata_CL`](../tables-index.md#alertsquarantinedata_cl), [`alertsremediationdata_CL`](../tables-index.md#alertsremediationdata_cl), [`alertssecurityassessmentdata_CL`](../tables-index.md#alertssecurityassessmentdata_cl), [`alertsubadata_CL`](../tables-index.md#alertsubadata_cl), [`eventsapplicationdata_CL`](../tables-index.md#eventsapplicationdata_cl), [`eventsauditdata_CL`](../tables-index.md#eventsauditdata_cl), [`eventsconnectiondata_CL`](../tables-index.md#eventsconnectiondata_cl), [`eventsincidentdata_CL`](../tables-index.md#eventsincidentdata_cl), [`eventsnetworkdata_CL`](../tables-index.md#eventsnetworkdata_cl), [`eventspagedata_CL`](../tables-index.md#eventspagedata_cl) |
| **Used in Solutions** | [Netskopev2](../solutions/netskopev2.md) |
| **Connector Definition Files** | [Netskope_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeDataConnector/Netskope_FunctionApp.json) |

The [Netskope](https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/) data connector provides the following capabilities: 

 1. NetskopeToAzureStorage : 

 >* Get the Netskope Alerts and Events data from Netskope and ingest to Azure storage. 

 2. StorageToSentinel : 

 >* Get the Netskope Alerts and Events data from Azure storage and ingest to custom log table in log analytics workspace. 

 3. WebTxMetrics : 

 >* Get the WebTxMetrics data from Netskope and ingest to custom log table in log analytics workspace.





 For more details of REST APIs refer to the below documentations: 

 1. Netskope API documentation: 

> https://docs.netskope.com/en/netskope-help/admin-console/rest-api/rest-api-v2-overview-312207/ 

 2. Azure storage documentation: 

> https://learn.microsoft.com/azure/storage/common/storage-introduction 

 3. Microsoft log analytic documentation: 

> https://learn.microsoft.com/azure/azure-monitor/logs/log-analytics-overview

[← Back to Connectors Index](../connectors-index.md)
