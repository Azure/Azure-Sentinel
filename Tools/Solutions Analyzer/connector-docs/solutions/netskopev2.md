# Netskopev2

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Netskope |
| **Support Tier** | Partner |
| **Support Link** | [https://www.netskope.com/services#support](https://www.netskope.com/services#support) |
| **Categories** | domains |
| **First Published** | 2024-03-18 |
| **Last Updated** | 2024-03-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [Netskope Alerts and Events](../connectors/netskopealertsevents.md)

**Publisher:** Netskope

Netskope Security Alerts and Events

| | |
|--------------------------|---|
| **Tables Ingested** | `NetskopeAlerts_CL` |
| | `NetskopeEventsApplication_CL` |
| | `NetskopeEventsAudit_CL` |
| | `NetskopeEventsConnection_CL` |
| | `NetskopeEventsDLP_CL` |
| | `NetskopeEventsEndpoint_CL` |
| | `NetskopeEventsInfrastructure_CL` |
| | `NetskopeEventsNetwork_CL` |
| | `NetskopeEventsPage_CL` |
| **Connector Definition Files** | [NetskopeAlertsEvents_ConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeAlertsEvents_RestAPI_CCP/NetskopeAlertsEvents_ConnectorDefination.json) |

[→ View full connector details](../connectors/netskopealertsevents.md)

### [Netskope Data Connector](../connectors/netskopedataconnector.md)

**Publisher:** Netskope

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

| | |
|--------------------------|---|
| **Tables Ingested** | `Netskope_WebTx_metrics_CL` |
| | `alertscompromisedcredentialdata_CL` |
| | `alertsctepdata_CL` |
| | `alertsdlpdata_CL` |
| | `alertsmalsitedata_CL` |
| | `alertsmalwaredata_CL` |
| | `alertspolicydata_CL` |
| | `alertsquarantinedata_CL` |
| | `alertsremediationdata_CL` |
| | `alertssecurityassessmentdata_CL` |
| | `alertsubadata_CL` |
| | `eventsapplicationdata_CL` |
| | `eventsauditdata_CL` |
| | `eventsconnectiondata_CL` |
| | `eventsincidentdata_CL` |
| | `eventsnetworkdata_CL` |
| | `eventspagedata_CL` |
| **Connector Definition Files** | [Netskope_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeDataConnector/Netskope_FunctionApp.json) |

[→ View full connector details](../connectors/netskopedataconnector.md)

### [Netskope Web Transactions Data Connector](../connectors/netskopewebtransactionsdataconnector.md)

**Publisher:** Netskope

The [Netskope Web Transactions](https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/) data connector provides the functionality of a docker image to pull the Netskope Web Transactions data from google pubsublite, process the data and ingest the processed data to Log Analytics. As part of this data connector two tables will be formed in Log Analytics, one for Web Transactions data and other for errors encountered during execution.





 For more details related to Web Transactions refer to the below documentation: 

 1. Netskope Web Transactions documentation: 

> https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/ 



| | |
|--------------------------|---|
| **Tables Ingested** | `NetskopeWebtxData_CL` |
| | `NetskopeWebtxErrors_CL` |
| **Connector Definition Files** | [Netskope_WebTransactions.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeWebTransactionsDataConnector/Netskope_WebTransactions.json) |

[→ View full connector details](../connectors/netskopewebtransactionsdataconnector.md)

## Tables Reference

This solution ingests data into **28 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NetskopeAlerts_CL` | Netskope Alerts and Events |
| `NetskopeEventsApplication_CL` | Netskope Alerts and Events |
| `NetskopeEventsAudit_CL` | Netskope Alerts and Events |
| `NetskopeEventsConnection_CL` | Netskope Alerts and Events |
| `NetskopeEventsDLP_CL` | Netskope Alerts and Events |
| `NetskopeEventsEndpoint_CL` | Netskope Alerts and Events |
| `NetskopeEventsInfrastructure_CL` | Netskope Alerts and Events |
| `NetskopeEventsNetwork_CL` | Netskope Alerts and Events |
| `NetskopeEventsPage_CL` | Netskope Alerts and Events |
| `NetskopeWebtxData_CL` | Netskope Web Transactions Data Connector |
| `NetskopeWebtxErrors_CL` | Netskope Web Transactions Data Connector |
| `Netskope_WebTx_metrics_CL` | Netskope Data Connector |
| `alertscompromisedcredentialdata_CL` | Netskope Data Connector |
| `alertsctepdata_CL` | Netskope Data Connector |
| `alertsdlpdata_CL` | Netskope Data Connector |
| `alertsmalsitedata_CL` | Netskope Data Connector |
| `alertsmalwaredata_CL` | Netskope Data Connector |
| `alertspolicydata_CL` | Netskope Data Connector |
| `alertsquarantinedata_CL` | Netskope Data Connector |
| `alertsremediationdata_CL` | Netskope Data Connector |
| `alertssecurityassessmentdata_CL` | Netskope Data Connector |
| `alertsubadata_CL` | Netskope Data Connector |
| `eventsapplicationdata_CL` | Netskope Data Connector |
| `eventsauditdata_CL` | Netskope Data Connector |
| `eventsconnectiondata_CL` | Netskope Data Connector |
| `eventsincidentdata_CL` | Netskope Data Connector |
| `eventsnetworkdata_CL` | Netskope Data Connector |
| `eventspagedata_CL` | Netskope Data Connector |

[← Back to Solutions Index](../solutions-index.md)
