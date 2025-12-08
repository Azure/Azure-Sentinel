# Netskope Web Transactions Data Connector

| | |
|----------|-------|
| **Connector ID** | `NetskopeWebTransactionsDataConnector` |
| **Publisher** | Netskope |
| **Tables Ingested** | [`NetskopeWebtxData_CL`](../tables-index.md#netskopewebtxdata_cl), [`NetskopeWebtxErrors_CL`](../tables-index.md#netskopewebtxerrors_cl) |
| **Used in Solutions** | [Netskopev2](../solutions/netskopev2.md) |
| **Connector Definition Files** | [Netskope_WebTransactions.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeWebTransactionsDataConnector/Netskope_WebTransactions.json) |

The [Netskope Web Transactions](https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/) data connector provides the functionality of a docker image to pull the Netskope Web Transactions data from google pubsublite, process the data and ingest the processed data to Log Analytics. As part of this data connector two tables will be formed in Log Analytics, one for Web Transactions data and other for errors encountered during execution.





 For more details related to Web Transactions refer to the below documentation: 

 1. Netskope Web Transactions documentation: 

> https://docs.netskope.com/en/netskope-help/data-security/transaction-events/netskope-transaction-events/ 



[← Back to Connectors Index](../connectors-index.md)
