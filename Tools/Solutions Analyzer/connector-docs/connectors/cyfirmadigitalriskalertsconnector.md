# CYFIRMA Digital Risk

| | |
|----------|-------|
| **Connector ID** | `CyfirmaDigitalRiskAlertsConnector` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CyfirmaDBWMDarkWebAlerts_CL`](../tables-index.md#cyfirmadbwmdarkwebalerts_cl), [`CyfirmaDBWMPhishingAlerts_CL`](../tables-index.md#cyfirmadbwmphishingalerts_cl), [`CyfirmaDBWMRansomwareAlerts_CL`](../tables-index.md#cyfirmadbwmransomwarealerts_cl), [`CyfirmaSPEConfidentialFilesAlerts_CL`](../tables-index.md#cyfirmaspeconfidentialfilesalerts_cl), [`CyfirmaSPEPIIAndCIIAlerts_CL`](../tables-index.md#cyfirmaspepiiandciialerts_cl), [`CyfirmaSPESocialThreatAlerts_CL`](../tables-index.md#cyfirmaspesocialthreatalerts_cl), [`CyfirmaSPESourceCodeAlerts_CL`](../tables-index.md#cyfirmaspesourcecodealerts_cl) |
| **Used in Solutions** | [Cyfirma Digital Risk](../solutions/cyfirma-digital-risk.md) |
| **Connector Definition Files** | [CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Data%20Connectors/CyfirmaDigitalRiskAlerts_ccp/CyfirmaDigitalRiskAlerts_DataConnectorDefinition.json) |

The CYFIRMA Digital Risk Alerts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR Alerts API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

[← Back to Connectors Index](../connectors-index.md)
