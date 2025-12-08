# Rubrik Security Cloud data connector

| | |
|----------|-------|
| **Connector ID** | `RubrikSecurityCloudAzureFunctions` |
| **Publisher** | Rubrik, Inc |
| **Tables Ingested** | [`Rubrik_Anomaly_Data_CL`](../tables-index.md#rubrik_anomaly_data_cl), [`Rubrik_Events_Data_CL`](../tables-index.md#rubrik_events_data_cl), [`Rubrik_Ransomware_Data_CL`](../tables-index.md#rubrik_ransomware_data_cl), [`Rubrik_ThreatHunt_Data_CL`](../tables-index.md#rubrik_threathunt_data_cl) |
| **Used in Solutions** | [RubrikSecurityCloud](../solutions/rubriksecuritycloud.md) |
| **Connector Definition Files** | [RubrikWebhookEvents_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Data%20Connectors/RubrikWebhookEvents/RubrikWebhookEvents_FunctionApp.json) |

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik's Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

[← Back to Connectors Index](../connectors-index.md)
